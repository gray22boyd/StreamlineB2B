# Analytics Agent - Setup Guide

## 📋 Quick Setup Steps

Follow these steps to get your Analytics Agent running:

### Step 1: Set Up Database Tables

1. Open your Supabase SQL Editor (or psql/pgAdmin)

2. Run these SQL files in order:
   ```sql
   -- Create tables
   \i database/migrations/create_analytics_demo_tables.sql
   
   -- Insert customers and products
   \i database/migrations/insert_analytics_demo_data.sql
   
   -- Insert orders
   \i database/migrations/insert_analytics_demo_orders.sql
   
   -- Insert order items
   \i database/migrations/insert_analytics_demo_order_items.sql
   ```

   Or copy/paste the contents directly into Supabase SQL Editor.

### Step 2: Verify Data

Check that data was inserted successfully:

```sql
-- Should return 20
SELECT COUNT(*) FROM analytics_demo_customers;

-- Should return 50
SELECT COUNT(*) FROM analytics_demo_products;

-- Should return 31
SELECT COUNT(*) FROM analytics_demo_orders;

-- Should return inventory count
SELECT COUNT(*) FROM analytics_demo_inventory;
```

### Step 3: Test the Agent

Run the interactive chat interface:

```bash
# Make sure you're in the project root
cd C:\Users\gray2\Downloads\StreamlineAgents

# Run the interactive chat
python -m agents.analytics_agent.chat
```

### Step 4: Try Sample Questions

Once in the chat, try these:

```
stats                                    # Quick overview
top                                      # Top products
customers                                # Customer insights
What was our total revenue?              # Natural language
Which products sold the most?            # Natural language
Show me Gold tier customers              # Natural language
```

### Step 5: Start MCP Server (Optional)

For HTTP API access:

```bash
python -m agents.analytics_agent.mcp_server
```

Server will run on `http://localhost:8020`

Test with curl:
```bash
# Health check
curl http://localhost:8020/health

# List tools
curl http://localhost:8020/mcp/tools

# Call a tool (with auth token if set)
curl -X POST http://localhost:8020/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "get_quick_stats",
      "arguments": {}
    }
  }'
```

## 🔍 Troubleshooting

### Database Connection Issues

If you get `connection refused` errors:

1. Check your `.env` file has correct `DATABASE_URL`
2. Test connection: `psql $DATABASE_URL`
3. Verify firewall isn't blocking the connection

### OpenAI API Issues

If you get API errors:

1. Verify `OPENAI_API_KEY` is in `.env`
2. Check API key is valid at https://platform.openai.com/api-keys
3. Ensure you have credits available

### Import Errors

If you get `ModuleNotFoundError`:

```bash
# Install dependencies
pip install openai psycopg2-binary python-dotenv

# Or if using requirements.txt
pip install -r requirements.txt
```

## 🎯 Next Steps

Once testing is complete:

1. ✅ Verify all tools work correctly
2. ✅ Test with various questions
3. ✅ Check SQL generation quality
4. ✅ Review security (read-only access)
5. 🔲 Integrate with frontend (wait for your approval)
6. 🔲 Add to agent registry
7. 🔲 Deploy MCP server to production

## 📊 Demo Business Context

The fake data represents:

**Business:** Pacific Northwest Retail Store
- **Location:** Oregon and Washington
- **Product Categories:** Electronics, Home & Kitchen, Clothing, Sports, Books
- **Time Period:** May - October 2024 (6 months)
- **Scale:** 100 customers, 50 products, ~300 orders

This gives enough data to answer most analytical questions while keeping the demo lightweight.

## ❓ Common Questions

**Q: Can I use this with my real business data?**
A: Yes! Just point it to different tables and update the schema context. The SQL generation adapts to any schema.

**Q: Is it safe to use in production?**
A: The agent has read-only safeguards, but always:
- Use a read-only database user
- Review generated SQL queries
- Set up proper authentication
- Monitor API usage costs

**Q: How accurate is the SQL generation?**
A: Very good for standard queries. Complex queries might need refinement. Always test before relying on results.

**Q: Can I customize the LLM?**
A: Yes! Edit `tools.py` and change the model in `_generate_sql_query()` and `_format_results()`.

**Q: What if I need more demo data?**
A: Edit the SQL insert files to add more customers, products, and orders. Follow the same patterns.

---

**Need help?** Review the full README in `agents/analytics_agent/README.md`

**Ready to integrate?** Let me know when testing is complete and you want to connect it to the frontend!

