# agents/analytics_agent/schemas.py
"""
MCP Tool Schemas for Analytics Agent
Defines the structure and documentation for all analytics tools
"""

# Tool descriptions for MCP
TOOL_DESCRIPTIONS = {
    "query_database": "Ask any question about the business data in natural language. The agent will generate and execute appropriate SQL queries to answer your question.",
    "get_quick_stats": "Get a quick overview of key business metrics including total customers, orders, revenue, and average order value.",
    "get_top_products": "Retrieve the top-selling products ranked by revenue, with details on units sold and order counts.",
    "get_customer_insights": "Get insights about customer segments by loyalty tier or detailed information about a specific customer."
}

# MCP Tool Schemas (JSON Schema format)
MCP_TOOL_SCHEMAS = {
    "query_database": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "Natural language question about the business data (e.g., 'What were our total sales last month?', 'Who are our top 5 customers?', 'Which products are low in stock?')"
            }
        },
        "required": ["question"]
    },
    
    "get_quick_stats": {
        "type": "object",
        "properties": {},
        "required": []
    },
    
    "get_top_products": {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Number of top products to return (default: 10, max: 50)",
                "default": 10,
                "minimum": 1,
                "maximum": 50
            }
        },
        "required": []
    },
    
    "get_customer_insights": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "Optional UUID of a specific customer. If not provided, returns insights by customer segments.",
                "format": "uuid"
            }
        },
        "required": []
    }
}

# Example queries for documentation/testing
EXAMPLE_QUESTIONS = [
    "What was our total revenue last month?",
    "Which products are selling the best?",
    "Who are our top 10 customers by lifetime value?",
    "What's the average order value?",
    "Which products are low in stock?",
    "How many orders did we have this week?",
    "What are the most popular product categories?",
    "Which customers haven't ordered in the last 30 days?",
    "What's our revenue trend over the past 6 months?",
    "Which payment method is most common?",
    "How many Gold tier customers do we have?",
    "What's the average discount percentage?",
    "Which products have the highest profit margin?",
    "How many orders were cancelled this month?",
    "Which warehouse location has the most inventory?"
]

