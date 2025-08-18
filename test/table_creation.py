import os
import psycopg2
from dotenv import load_dotenv
from utils.supa import SupabaseClient

load_dotenv()


def test_connection():
    try:
        supabase = SupabaseClient(customer_schema="Legends")
        cur = supabase.cur

        print(f"✅ Connected to {supabase.customer_schema} Supabase!")

        supabase.commit()
        supabase.close()
        print("✅ Table created successfully!")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

def test_gather_tables():
    supabase = SupabaseClient(customer_schema="Legends")
    cur = supabase.cur
    result = cur.fetchall()
    supabase.close()
    return result

if __name__ == "__main__":
    test_connection()