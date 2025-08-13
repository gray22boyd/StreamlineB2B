import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def test_connection():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()

        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"✅ Connected to Supabase!")
        print(f"PostgreSQL version: {version[0][:50]}...")

        cur.close()
        conn.close()
        print("✅ Connection test successful!")

    except Exception as e:
        print(f"❌ Connection failed: {e}")


if __name__ == "__main__":
    test_connection()