import os
import psycopg2
from dotenv import load_dotenv
from utils.supa import SupabaseClient
from utils.pdf_chunker import process_pdf

load_dotenv()


def test_gather_tables():
    supabase = SupabaseClient(customer_schema="Legends")
    cur = supabase.cur

    print(f"✅ Connected to Supabase!")

    result = supabase.gather_tables()
    supabase.close()
    return result

def test_upload_to_table(pdf_path: str):
    supabase = SupabaseClient(customer_schema="Legends")
    chunks, embeddings = process_pdf(pdf_path)

    supabase.upload_to_table(table_name="embeddings", data=chunks)

print(test_gather_tables())










