import os
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras

load_dotenv()

class SupabaseClient:
    def __init__(self, customer_schema: str = "public"):
        self.customer_schema = customer_schema
        self.conn = psycopg2.connect(
            os.getenv('DATABASE_URL'),
            cursor_factory=psycopg2.extras.RealDictCursor  # Better for UUIDs
        )
        self.cur = self.conn.cursor()
        
        # Set the search path to use the specified schema
        if customer_schema != "public":
            self.cur.execute(f"SET search_path TO {customer_schema}, public")

    def close(self):
        self.cur.close()
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()







