import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv('DATABASE_URL')

def list_tables():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("""
    SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def pull_data_from_db(query: str, table: str) -> list[dict]:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    cur.execute("""
    SELECT text_content FROM {table} ORDER BY embedding <-> LIMIT 2
    """)
    result = cur.fetchall()

    print(result)

    cur.close()
    conn.close()
    return result


def main():
    print(pull_data_from_db("What is the total distance of the course?", ""))