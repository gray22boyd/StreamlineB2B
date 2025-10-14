# agents/analytics_agent/tools.py

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class AnalyticsTools:
    """
    Intelligent analytics agent that converts natural language questions
    into SQL queries and returns insights from the business database.
    """
    
    def __init__(self, business_id=None):
        """Initialize analytics tools with database connection"""
        self.business_id = business_id
        self.db_connection = psycopg2.connect(os.getenv('DATABASE_URL'))
        
        # Initialize OpenAI client for SQL generation
        self.llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Cache database schema
        self._db_schema = self._get_database_schema()
    
    def _get_database_schema(self):
        """Retrieve the schema of analytics demo tables"""
        schema_query = """
        SELECT 
            table_name,
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' 
        AND table_name LIKE 'analytics_demo_%'
        ORDER BY table_name, ordinal_position;
        """
        
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(schema_query)
                columns = cur.fetchall()
                
                # Organize schema by table
                schema = {}
                for col in columns:
                    table = col['table_name']
                    if table not in schema:
                        schema[table] = []
                    schema[table].append({
                        'column': col['column_name'],
                        'type': col['data_type'],
                        'nullable': col['is_nullable']
                    })
                
                return schema
        except Exception as e:
            print(f"Error retrieving schema: {e}")
            return {}
    
    def _get_schema_description(self):
        """Format schema for LLM context"""
        description = "# Database Schema for Retail Business Analytics\n\n"
        
        table_descriptions = {
            'analytics_demo_customers': 'Customer information including name, email, loyalty tier, and location',
            'analytics_demo_products': 'Product catalog with names, categories, SKUs, prices, and costs',
            'analytics_demo_orders': 'Order transactions with totals, dates, status, and payment methods',
            'analytics_demo_order_items': 'Individual line items for each order with quantities and prices',
            'analytics_demo_inventory': 'Current inventory levels and warehouse locations'
        }
        
        for table, columns in self._db_schema.items():
            desc = table_descriptions.get(table, 'Table description')
            description += f"## {table}\n{desc}\n\nColumns:\n"
            for col in columns:
                description += f"- {col['column']} ({col['type']})\n"
            description += "\n"
        
        return description
    
    def _generate_sql_query(self, question: str) -> str:
        """Use LLM to generate SQL from natural language question"""
        
        schema_context = self._get_schema_description()
        
        system_prompt = f"""You are an expert SQL query generator for a retail business analytics database.

{schema_context}

Generate ONLY a valid PostgreSQL SELECT query based on the user's question.
Follow these rules:
1. Return ONLY the SQL query, no explanations or markdown
2. Use only SELECT statements (no INSERT, UPDATE, DELETE, DROP, etc.)
3. Use appropriate JOINs when data spans multiple tables
4. Format currency with 2 decimal places using ROUND()
5. Use proper aggregations (SUM, COUNT, AVG) as needed
6. Add ORDER BY clauses for ranked results
7. Include LIMIT when showing top N results
8. Use COALESCE for null handling
9. Filter out cancelled orders unless specifically asked about them
10. For date ranges, use appropriate date functions

Return just the SQL query without any formatting or explanation."""

        try:
            response = self.llm.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.1
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            
            return sql_query
            
        except Exception as e:
            raise Exception(f"SQL generation failed: {str(e)}")
    
    def _validate_sql_query(self, query: str) -> bool:
        """Basic safety validation for SQL queries"""
        query_upper = query.upper()
        
        # Forbidden keywords that could modify data
        forbidden = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 
                    'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE']
        
        for keyword in forbidden:
            if keyword in query_upper:
                return False
        
        # Must be a SELECT query
        if not query_upper.strip().startswith('SELECT'):
            return False
        
        return True
    
    def _execute_query(self, query: str):
        """Execute SQL query and return results"""
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                results = cur.fetchall()
                
                # Convert to list of dicts for JSON serialization
                return [dict(row) for row in results]
                
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    def _format_results(self, results: list, question: str) -> str:
        """Format query results into human-readable response"""
        if not results:
            return "No data found for your query."
        
        # Use LLM to create natural language summary
        try:
            data_sample = json.dumps(results[:10], indent=2, default=str)  # Limit to first 10 rows
            
            summary_prompt = f"""Based on this query result, provide a clear, natural language summary.

Original question: {question}

Query results (showing first 10 rows):
{data_sample}

Total rows returned: {len(results)}

Provide:
1. A brief answer to the question
2. Key insights from the data
3. Any notable patterns or trends

Keep the response concise and business-focused."""

            response = self.llm.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a business analyst providing insights from data."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Append raw data if results are small
            if len(results) <= 20:
                summary += f"\n\n**Detailed Data:**\n```json\n{json.dumps(results, indent=2, default=str)}\n```"
            
            return summary
            
        except Exception as e:
            # Fallback to raw data if formatting fails
            return f"Query returned {len(results)} results:\n\n{json.dumps(results[:10], indent=2, default=str)}"
    
    def query_database(self, question: str) -> dict:
        """
        MCP Tool: Answer business questions by querying the analytics database
        
        Args:
            question: Natural language question about the business data
            
        Returns:
            Dict with success status, answer, SQL query used, and any errors
        """
        try:
            # Generate SQL from question
            sql_query = self._generate_sql_query(question)
            
            # Validate query for safety
            if not self._validate_sql_query(sql_query):
                return {
                    'success': False,
                    'error': 'Generated query failed safety validation',
                    'question': question
                }
            
            # Execute query
            results = self._execute_query(sql_query)
            
            # Format results
            answer = self._format_results(results, question)
            
            return {
                'success': True,
                'question': question,
                'answer': answer,
                'sql_query': sql_query,
                'row_count': len(results),
                'data': results if len(results) <= 100 else results[:100]  # Limit data returned
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'question': question
            }
    
    def get_quick_stats(self) -> dict:
        """
        MCP Tool: Get quick overview statistics about the business
        
        Returns:
            Dict with key business metrics
        """
        try:
            stats_query = """
            WITH stats AS (
                SELECT 
                    COUNT(DISTINCT c.id) as total_customers,
                    COUNT(DISTINCT p.id) as total_products,
                    COUNT(DISTINCT o.id) as total_orders,
                    COUNT(DISTINCT CASE WHEN o.status = 'completed' THEN o.id END) as completed_orders,
                    ROUND(SUM(CASE WHEN o.status = 'completed' THEN o.total_amount ELSE 0 END), 2) as total_revenue,
                    ROUND(AVG(CASE WHEN o.status = 'completed' THEN o.total_amount END), 2) as avg_order_value,
                    COUNT(DISTINCT o.customer_id) as customers_with_orders,
                    MAX(o.order_date) as last_order_date
                FROM analytics_demo_customers c
                CROSS JOIN analytics_demo_products p
                LEFT JOIN analytics_demo_orders o ON TRUE
            )
            SELECT * FROM stats;
            """
            
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(stats_query)
                stats = dict(cur.fetchone())
            
            return {
                'success': True,
                'stats': stats,
                'message': 'Quick statistics retrieved successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_top_products(self, limit: int = 10) -> dict:
        """
        MCP Tool: Get top selling products by revenue
        
        Args:
            limit: Number of top products to return (default 10)
            
        Returns:
            Dict with top products and their metrics
        """
        try:
            query = f"""
            SELECT 
                p.product_name,
                p.category,
                p.brand,
                COUNT(DISTINCT oi.order_id) as order_count,
                SUM(oi.quantity) as total_units_sold,
                ROUND(SUM(oi.subtotal), 2) as total_revenue,
                ROUND(AVG(oi.unit_price), 2) as avg_selling_price
            FROM analytics_demo_products p
            JOIN analytics_demo_order_items oi ON p.id = oi.product_id
            JOIN analytics_demo_orders o ON oi.order_id = o.id
            WHERE o.status = 'completed'
            GROUP BY p.id, p.product_name, p.category, p.brand
            ORDER BY total_revenue DESC
            LIMIT {limit};
            """
            
            results = self._execute_query(query)
            
            return {
                'success': True,
                'top_products': results,
                'count': len(results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_customer_insights(self, customer_id: str = None) -> dict:
        """
        MCP Tool: Get insights about customers or a specific customer
        
        Args:
            customer_id: Optional UUID of specific customer
            
        Returns:
            Dict with customer insights
        """
        try:
            if customer_id:
                query = f"""
                SELECT 
                    c.customer_name,
                    c.email,
                    c.loyalty_tier,
                    c.city,
                    c.state,
                    c.customer_since,
                    COUNT(o.id) as total_orders,
                    COUNT(CASE WHEN o.status = 'completed' THEN 1 END) as completed_orders,
                    ROUND(SUM(CASE WHEN o.status = 'completed' THEN o.total_amount ELSE 0 END), 2) as lifetime_value,
                    ROUND(AVG(CASE WHEN o.status = 'completed' THEN o.total_amount END), 2) as avg_order_value,
                    MAX(o.order_date) as last_order_date
                FROM analytics_demo_customers c
                LEFT JOIN analytics_demo_orders o ON c.id = o.customer_id
                WHERE c.id = '{customer_id}'
                GROUP BY c.id, c.customer_name, c.email, c.loyalty_tier, c.city, c.state, c.customer_since;
                """
            else:
                query = """
                SELECT 
                    c.loyalty_tier,
                    COUNT(DISTINCT c.id) as customer_count,
                    COUNT(o.id) as total_orders,
                    ROUND(AVG(o.total_amount), 2) as avg_order_value,
                    ROUND(SUM(o.total_amount), 2) as total_revenue
                FROM analytics_demo_customers c
                LEFT JOIN analytics_demo_orders o ON c.id = o.customer_id AND o.status = 'completed'
                GROUP BY c.loyalty_tier
                ORDER BY total_revenue DESC;
                """
            
            results = self._execute_query(query)
            
            return {
                'success': True,
                'customer_insights': results,
                'count': len(results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'db_connection'):
            self.db_connection.close()


# Factory function for creating analytics tools
def create_analytics_tools(business_id=None):
    """Factory function to create analytics tools for a specific business"""
    return AnalyticsTools(business_id)

