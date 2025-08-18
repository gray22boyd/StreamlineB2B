from fastmcp import FastMCP
from utils.Rag import pull_data_from_db
from utils.Rag import list_tables
from utils.supa import SupabaseClient

schema = "Legends"
naming_convention = "customer_service"
supabase = SupabaseClient(customer_schema=schema)

@mcp.tool
def pull_tables_from_db(query: str):
    """
    Pull a list of tables from the supabase database that are for public facing use.
    """
    supabase = SupabaseClient(customer_schema=schema)
    supabase.cur.execute(f"SELECT {supabase.customer_schema}.{naming_convention}_table_name FROM information_schema.tables WHERE table_schema = 'public';")
    return supabase.cur.fetchall()


