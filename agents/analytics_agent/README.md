# Analytics Agent

Intelligent database insights agent that answers business questions using natural language. Built with MCP (Model Context Protocol) for modular integration.

## 🎯 Overview

The Analytics Agent is designed to help businesses extract insights from their data without writing SQL. It:

- **Converts natural language to SQL**: Ask questions in plain English
- **Generates dynamic queries**: No hardcoded queries - fully intelligent
- **Provides actionable insights**: Returns formatted, business-friendly answers
- **Ensures data safety**: Read-only access with query validation
- **Integrates via MCP**: Works as a standalone service or in-process

## 📁 File Structure

```
analytics_agent/
├── __init__.py           # Package initialization
├── tools.py              # Core analytics tools with SQL generation
├── schemas.py            # MCP tool schemas and definitions
├── mcp_server.py         # HTTP MCP server for remote access
├── chat.py               # Interactive CLI for testing
└── README.md             # This file
```

## 🗄️ Demo Database

The agent uses a fake retail business database with these tables:

- **analytics_demo_customers**: Customer information (100 customers)
- **analytics_demo_products**: Product catalog (50 products across 5 categories)
- **analytics_demo_orders**: Order transactions (6 months of data)
- **analytics_demo_order_items**: Order line items
- **analytics_demo_inventory**: Current inventory levels

### Database Setup

1. Run the schema creation script:
```sql
-- In your Supabase SQL editor or psql:
\i database/migrations/create_analytics_demo_tables.sql
```

2. Insert demo data:
```sql
\i database/migrations/insert_analytics_demo_data.sql
\i database/migrations/insert_analytics_demo_orders.sql
\i database/migrations/insert_analytics_demo_order_items.sql
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database (Supabase recommended)
- OpenAI API key

### Environment Variables

Add to your `.env` file:

```env
DATABASE_URL=postgresql://user:password@host:port/database
OPENAI_API_KEY=sk-your-key-here

# Optional: For MCP server authentication
MCP_AUTH_TOKEN=your-secret-token
MCP_HOST=0.0.0.0
MCP_PORT=8020
```

### Testing with Interactive Chat

The easiest way to test the agent:

```bash
python -m agents.analytics_agent.chat
```

This launches an interactive CLI where you can:
- Ask natural language questions
- View SQL queries generated
- See formatted results
- Test all agent capabilities

### Example Questions

```
You: What was our total revenue last month?
You: Who are our top 5 customers by lifetime value?
You: Which products are low in stock?
You: Show me revenue trends over the past 6 months
You: What's the most popular product category?
```

### Special Commands

- `stats` - Quick business overview
- `top` - Top selling products
- `customers` - Customer insights by tier
- `examples` - See more example questions
- `help` - Show all commands
- `quit` - Exit

## 🔧 Usage Modes

### Mode 1: In-Process (For Testing)

```python
from agents.analytics_agent.tools import AnalyticsTools

# Create analytics instance
analytics = AnalyticsTools()

# Ask a question
result = analytics.query_database("What were our sales last week?")
print(result['answer'])

# Get quick stats
stats = analytics.get_quick_stats()
print(stats)

# Get top products
top = analytics.get_top_products(limit=10)
print(top)
```

### Mode 2: MCP Server (For Production)

Run as a standalone HTTP service:

```bash
python -m agents.analytics_agent.mcp_server
```

Server runs on `http://localhost:8020` with these endpoints:

- `GET /health` - Health check
- `GET /mcp/tools` - List available tools
- `POST /mcp` - Execute tool calls

### Mode 3: Frontend Integration

The agent will integrate with your web app like other agents:

```python
# In frontend/agent_registry.py
class AnalyticsAgentAdapter(AgentAdapter):
    # ... adapter implementation
```

## 🛠️ Available Tools

### 1. query_database

Ask any question about the business data.

**Arguments:**
- `question` (string, required): Natural language question

**Example:**
```python
result = analytics.query_database("Which customers ordered in the last 7 days?")
```

### 2. get_quick_stats

Get overview of key business metrics.

**Arguments:** None

**Returns:**
- Total customers
- Total products
- Total orders
- Completed orders
- Total revenue
- Average order value
- Last order date

### 3. get_top_products

Get top-selling products by revenue.

**Arguments:**
- `limit` (integer, optional): Number of products (default: 10, max: 50)

**Returns:**
- Product name, category, brand
- Order count
- Units sold
- Total revenue
- Average selling price

### 4. get_customer_insights

Get customer segment insights or specific customer details.

**Arguments:**
- `customer_id` (UUID, optional): Specific customer ID

**Returns:**
- By segment: Customer counts, orders, revenue by loyalty tier
- By customer: Individual customer details and purchase history

## 🔐 Security

The agent implements multiple safety layers:

1. **Read-Only Queries**: Only SELECT statements allowed
2. **Query Validation**: Blocks INSERT, UPDATE, DELETE, DROP, etc.
3. **Authentication**: Optional token-based auth for MCP server
4. **SQL Injection Prevention**: Uses parameterized queries where possible
5. **Result Limiting**: Caps result sizes to prevent memory issues

## 📊 Sample Data Schema

**Customers:**
- 100 customers across OR and WA
- 4 loyalty tiers: Bronze, Silver, Gold, Platinum
- Various join dates over 6 months

**Products:**
- 50 products in 5 categories
  - Electronics (10)
  - Home & Kitchen (10)
  - Clothing (10)
  - Sports & Outdoors (10)
  - Books & Media (10)

**Orders:**
- ~300 orders from May - October 2024
- Mix of completed and cancelled
- Various payment methods
- Realistic discounts and totals

## 🧪 Testing Checklist

Before integrating with frontend:

- [ ] Database tables created successfully
- [ ] Demo data inserted
- [ ] Interactive chat works
- [ ] Natural language questions generate valid SQL
- [ ] Results are formatted correctly
- [ ] Quick stats tool works
- [ ] Top products tool works
- [ ] Customer insights tool works
- [ ] MCP server starts and responds to requests
- [ ] Authentication works (if enabled)

## 🐛 Troubleshooting

**"DATABASE_URL not set"**
- Add `DATABASE_URL` to your `.env` file
- Format: `postgresql://user:password@host:port/database`

**"OPENAI_API_KEY not set"**
- Add your OpenAI API key to `.env`
- Get one at: https://platform.openai.com/api-keys

**"No data found"**
- Verify demo data was inserted: `SELECT COUNT(*) FROM analytics_demo_orders;`
- Check table names match: `\dt analytics_demo*`

**"SQL generation failed"**
- Check OpenAI API key is valid
- Verify API has credits
- Check network connectivity

**"Permission denied"**
- Ensure database user has SELECT permissions on analytics tables
- Grant if needed: `GRANT SELECT ON ALL TABLES IN SCHEMA public TO your_user;`

## 🔮 Future Enhancements

Potential improvements:

- [ ] Query result caching for common questions
- [ ] Data visualization generation (charts/graphs)
- [ ] Multi-database support
- [ ] Custom business logic injection
- [ ] Scheduled reports
- [ ] Export to CSV/Excel
- [ ] Natural language query history
- [ ] Query performance optimization suggestions

## 📝 Notes

- The agent uses GPT-4o-mini for cost-effective SQL generation
- Temperature is set low (0.1) for consistent query generation
- Results are summarized using LLM for better user experience
- Demo data is intentionally simple but realistic
- Schema can be extended for real business needs

---

**Ready to integrate?** Contact the team when testing is complete!



