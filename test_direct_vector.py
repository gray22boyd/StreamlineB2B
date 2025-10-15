#!/usr/bin/env python3
"""Test vector search directly"""

from utils.supa import SupabaseClient
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Generate a test embedding
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
embeddings = client.embeddings.create(
    input="Do you offer ongoing support?",
    model="text-embedding-3-small"
)
embedding = embeddings.data[0].embedding

print(f"Generated embedding with {len(embedding)} dimensions")
print(f"First 3 values: {embedding[:3]}")

# Connect to DB
supabase = SupabaseClient(customer_schema="public")

# Format embedding as string for pgvector
embedding_str = '[' + ','.join(str(x) for x in embedding) + ']'
print(f"\nEmbedding string format (first 100 chars): {embedding_str[:100]}...")

# Try different query formats
print("\n" + "="*60)
print("TEST 1: Direct vector literal")
print("="*60)
try:
    supabase.cur.execute("""
        SELECT COUNT(*) as count FROM assistant_knowledge_base
    """)
    total = supabase.cur.fetchone()['count']
    print(f"Total rows in table: {total}")
    
    supabase.cur.execute("""
        SELECT 
            id,
            chunk_type,
            LEFT(text_content, 50) as preview
        FROM assistant_knowledge_base
        ORDER BY embedding <=> %s::vector
        LIMIT 3
    """, (embedding_str,))
    
    results = supabase.cur.fetchall()
    print(f"Results: {len(results)}")
    for r in results:
        print(f"  - {r['chunk_type']}: {r['preview']}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("TEST 2: Using list directly")
print("="*60)
try:
    supabase.cur.execute("""
        SELECT 
            id,
            chunk_type,
            LEFT(text_content, 50) as preview
        FROM assistant_knowledge_base
        ORDER BY embedding <=> %s
        LIMIT 3
    """, (embedding,))
    
    results = supabase.cur.fetchall()
    print(f"Results: {len(results)}")
    for r in results:
        print(f"  - {r['chunk_type']}: {r['preview']}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("TEST 3: Check actual embedding in DB")
print("="*60)
try:
    supabase.cur.execute("""
        SELECT id, pg_typeof(embedding) as type_name
        FROM assistant_knowledge_base
        LIMIT 1
    """)
    result = supabase.cur.fetchone()
    print(f"Embedding type in DB: {result['type_name']}")
except Exception as e:
    print(f"Error: {e}")

supabase.close()

