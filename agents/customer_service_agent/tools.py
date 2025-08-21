from fastmcp import FastMCP
from utils.RAG import pull_data_from_db
from utils.RAG import list_tables
from utils.supa import SupabaseClient

schema = "Legends"
naming_convention = "customer_service"
supabase = SupabaseClient(customer_schema=schema)

class CustomerServiceTools:
    def pull_tables_from_db():
        """
        Pull a list of tables from the supabase database that are for public facing use.
        """
        supabase = SupabaseClient(customer_schema=schema)
        supabase.cur.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}' AND table_name LIKE '{naming_convention}%';")
        return supabase.cur.fetchall()

    def pull_relevant_chunks(query: str, table_name: str):
        """
        Pull a list of tables from the supabase database that are for public facing use.
        """
        relevant_chunks = pull_data_from_db(query, table_name)
        text = relevant_chunks[0]['text_content']
        return text


def main():
    print(CustomerServiceTools.pull_tables_from_db())
    print(CustomerServiceTools.pull_relevant_chunks("What is the total distance of the course?", "customer_service_embeddings"))

if __name__ == "__main__":
    main()