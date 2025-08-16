import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

class SupabaseClient:
    def __init__(self, customer_schema: str):
        self.conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()







