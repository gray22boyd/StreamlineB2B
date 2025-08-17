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

        print("✅ Connection test successful!")

        # Create tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                index int not null,
                embedding vector(3072),
                source_file text,
                chunk_number int,
                text_content text,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ Tables created successfully!")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Connection failed: {e}")


if __name__ == "__main__":
    test_connection()