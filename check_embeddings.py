#!/usr/bin/env python3
"""Check if embeddings are actually stored in the database"""

from utils.supa import SupabaseClient
from dotenv import load_dotenv

load_dotenv()

supabase = SupabaseClient(customer_schema="public")

# Check if embeddings are NULL
supabase.cur.execute("""
    SELECT 
        id,
        chunk_type,
        embedding IS NULL as is_null,
        LEFT(text_content, 50) as preview
    FROM assistant_knowledge_base
    LIMIT 5
""")

results = supabase.cur.fetchall()

print("Checking embeddings in database:")
print("="*60)

for r in results:
    print(f"\nID: {r['id']}")
    print(f"Type: {r['chunk_type']}")
    print(f"Preview: {r['preview']}...")
    print(f"Embedding is NULL: {r['is_null']}")

# Try to get first element of an embedding
print("\n" + "="*60)
print("Checking actual embedding data:")
supabase.cur.execute("SELECT id, embedding FROM assistant_knowledge_base LIMIT 1")
result = supabase.cur.fetchone()
if result:
    embedding = result['embedding']
    print(f"Embedding type: {type(embedding)}")
    print(f"Embedding value: {str(embedding)[:200]}...")
    if embedding:
        print(f"Embedding length: {len(embedding) if hasattr(embedding, '__len__') else 'N/A'}")

supabase.close()

