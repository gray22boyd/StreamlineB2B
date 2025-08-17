from fastmcp import FastMCP
from utils.Rag import pull_data_from_db
from utils.Rag import list_tables

schema = "Legends"

@mcp.tool
def pull_tables_from_db(query: str):
    """
    Pull a list of tables from the supabase database that are for public facing use.
    """
    supabase = SupabaseClient(customer_schema=schema)
    supabase.cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    return supabase.cur.fetchall()


