import os
import psycopg2
from dotenv import load_dotenv
from utils.supa import SupabaseClient

load_dotenv()



supabase = SupabaseClient()
cur = supabase.cur

cur.execute("SELECT version();")
version = cur.fetchone()
print(f"✅ Connected to Supabase!")
print(f"PostgreSQL version: {version[0][:50]}...")

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
print(cur.fetchall())

supabase.close()










