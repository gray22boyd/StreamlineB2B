import os
import psycopg2
from dotenv import load_dotenv
from utils.pdf_chunker import embed_chunks
from openai import OpenAI
from utils.supa import SupabaseClient

load_dotenv()

def embed_query(query: str):
    client = OpenAI()
    embeddings = client.embeddings.create(
        input=query,
        model="text-embedding-3-large"
    )
    return embeddings.data[0].embedding


def list_tables():
    supabase = SupabaseClient()
    cur = supabase.cur
    cur.execute("""
    SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'
    """)
    result = cur.fetchall()
    supabase.close()
    return result


def pull_data_from_db(query: str, table: str) -> list[dict]:
    supabase = SupabaseClient()
    cur = supabase.cur
    
    embedding = embed_query(query)

    cur.execute(f"""
    SELECT text_content FROM {table} ORDER BY embedding <-> '{embedding}' LIMIT 2
    """)
    result = cur.fetchall()

    supabase.close()
    return result


def main():
    print(pull_data_from_db("What is the total distance of the course?", "embeddings"))

if __name__ == "__main__":
    main()

    