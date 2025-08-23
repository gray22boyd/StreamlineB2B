from fastmcp import FastMCP
from utils.RAG import pull_data_from_db
from utils.RAG import list_tables
from utils.supa import SupabaseClient


class CustomerServiceTools:
    def __init__(self, schema):
        self.schema = schema
        self.naming_convention = "customer_service"
        self.supabase = SupabaseClient(customer_schema=schema)


    def pull_tables_from_db(self):
        """
        Pull a list of tables from the supabase database that are for public facing use.
        """
        self.supabase.cur.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{self.schema}' AND table_name LIKE '{self.naming_convention}%';")
        return self.supabase.cur.fetchall()

    def pull_relevant_chunks(self, query: str, table_name: str):
        """
        Pull a list of tables from the supabase database that are for public facing use.
        """
        self.supabase.cur.execute(f"SELECT text_content FROM {table_name} WHERE text_content LIKE '%{query}%';")
        return self.supabase.cur.fetchall()

