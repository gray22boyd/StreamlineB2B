import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values, RealDictCursor

load_dotenv()

class SupabaseTable:
    def __init__(self, table_name: str, columns: list[str]):
        self.table_name = table_name
        self.columns = columns

class SupabaseClient:
    def __init__(self, customer_schema: str = "public"):
        self.customer_schema = customer_schema
        self.conn = psycopg2.connect(
            os.getenv('DATABASE_URL'),
            cursor_factory=RealDictCursor  # Better for UUIDs
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

    def create_table(self, table_name: str, columns: list[str]):
        col_defs = sql.SQL(', ').join(sql.Identifier(col) for col in columns)
        q = sql.SQL("CREATE TABLE IF NOT EXISTS {}.{} ({});").format(
            sql.Identifier(self.customer_schema),
            sql.Identifier(table_name),
            col_defs
        )
        self.cur.execute(q)
        self.commit()

    def gather_tables(self, naming_convention: str = ""):
        self.cur.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{self.customer_schema}' AND table_name LIKE '{naming_convention}%';")
        return self.cur.fetchall()

    def gather_columns(self, table_name: str):
        q = sql.SQL("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                    """)
        self.cur.execute(q, (self.customer_schema, table_name))
        return [row["column_name"] for row in self.cur.fetchall()]

    def upload_to_table(self, table_name: str, data: list[dict]):
        columns = self.gather_columns(table_name)
        table = SupabaseTable(table_name, columns)
        q = sql.SQL("INSERT INTO {}.{} VALUES (%s);").format(
            sql.Identifier(self.customer_schema),
            sql.Identifier(table_name)
        )
        self.cur.executemany(q, data)
        self.commit()







