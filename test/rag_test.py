import os
import psycopg2
from dotenv import load_dotenv
from utils.pdf_chunker import embed_chunks
from openai import OpenAI

load_dotenv()

def embed_query(query: str):
    """Embed query using OpenAI's API."""
    client = OpenAI()
    embeddings = client.embeddings.create(
        input=[query],
        model="text-embedding-3-large"
    )
    return embeddings.data[0].embedding

query = "Is this course a good choice for beginners?"
embedding = embed_query(query)


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
        cur.execute(f"""
            SELECT text_content FROM embeddings ORDER BY embedding <-> '{embedding}' LIMIT 1
        """)
        conn.commit()
        print("✅ Tables queried successfully!")

        rows = cur.fetchall( )
        print(rows[0])

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Connection failed: {e}")


if __name__ == "__main__":
    test_connection()

