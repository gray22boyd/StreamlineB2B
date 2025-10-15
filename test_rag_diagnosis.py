#!/usr/bin/env python3
"""
RAG Diagnostic Test Script
Run this to find out what's wrong with the knowledge base retrieval
"""

import os
from dotenv import load_dotenv
from utils.supa import SupabaseClient
from openai import OpenAI

load_dotenv()

def test_database_connection():
    """Test if we can connect to the database"""
    print("\n" + "="*60)
    print("TEST 1: Database Connection")
    print("="*60)
    try:
        supabase = SupabaseClient(customer_schema="public")
        print("✅ Database connection successful")
        supabase.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_table_exists():
    """Test if the knowledge base table exists"""
    print("\n" + "="*60)
    print("TEST 2: Table Existence")
    print("="*60)
    try:
        supabase = SupabaseClient(customer_schema="public")
        supabase.cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'assistant_knowledge_base'
            ) as exists
        """)
        result = supabase.cur.fetchone()
        exists = result['exists'] if result else False
        if exists:
            print("✅ Table 'assistant_knowledge_base' exists")
        else:
            print("❌ Table 'assistant_knowledge_base' does NOT exist")
        supabase.close()
        return exists
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        return False


def test_data_count():
    """Test how many chunks are in the database"""
    print("\n" + "="*60)
    print("TEST 3: Data Count")
    print("="*60)
    try:
        supabase = SupabaseClient(customer_schema="public")
        supabase.cur.execute("SELECT COUNT(*) as count FROM assistant_knowledge_base")
        count = supabase.cur.fetchone()['count']
        print(f"📊 Total chunks in database: {count}")
        if count == 0:
            print("❌ No data in table! Knowledge base is empty!")
        else:
            print(f"✅ Found {count} chunks")
        supabase.close()
        return count
    except Exception as e:
        print(f"❌ Error counting data: {e}")
        return 0


def test_sample_data():
    """Show sample data from the table"""
    print("\n" + "="*60)
    print("TEST 4: Sample Data")
    print("="*60)
    try:
        supabase = SupabaseClient(customer_schema="public")
        supabase.cur.execute("""
            SELECT id, chunk_type, LEFT(text_content, 100) as preview, 
                   pg_typeof(embedding) as embedding_type
            FROM assistant_knowledge_base 
            LIMIT 3
        """)
        rows = supabase.cur.fetchall()
        for i, row in enumerate(rows, 1):
            print(f"\n--- Chunk {i} ---")
            print(f"ID: {row['id']}")
            print(f"Type: {row['chunk_type']}")
            print(f"Preview: {row['preview']}...")
            print(f"Embedding Type: {row['embedding_type']}")
        supabase.close()
        return True
    except Exception as e:
        print(f"❌ Error fetching sample data: {e}")
        return False


def test_embedding_generation():
    """Test if we can generate embeddings"""
    print("\n" + "="*60)
    print("TEST 5: Embedding Generation")
    print("="*60)
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        test_text = "Do you offer ongoing support?"
        print(f"Testing with: '{test_text}'")
        
        embeddings = client.embeddings.create(
            input=test_text,
            model="text-embedding-3-small"
        )
        embedding = embeddings.data[0].embedding
        print(f"✅ Generated embedding with {len(embedding)} dimensions")
        return embedding
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        return None


def test_similarity_search(embedding):
    """Test vector similarity search"""
    print("\n" + "="*60)
    print("TEST 6: Similarity Search")
    print("="*60)
    try:
        supabase = SupabaseClient(customer_schema="public")
        
        print(f"Embedding dimensions: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        
        # Check what's in the database
        supabase.cur.execute("SELECT id, chunk_type, LEFT(text_content, 50) as preview FROM assistant_knowledge_base LIMIT 3")
        samples = supabase.cur.fetchall()
        print(f"\nSample data in DB:")
        for s in samples:
            print(f"  - {s['chunk_type']}: {s['preview']}...")
        
        # Try the search with explicit cast
        print("\n🔍 Attempting vector similarity search...")
        supabase.cur.execute("""
            SELECT 
                text_content,
                chunk_type,
                embedding <=> %s::vector as distance
            FROM assistant_knowledge_base
            ORDER BY embedding <=> %s::vector
            LIMIT 5
        """, (embedding, embedding))
        
        results = supabase.cur.fetchall()
        print(f"📊 Found {len(results)} results")
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"\n--- Result {i} ---")
                print(f"Type: {result['chunk_type']}")
                print(f"Distance: {result['distance']:.4f}")
                print(f"Content: {result['text_content'][:150]}...")
        else:
            print("⚠️ Query returned 0 results even though table has data!")
            print("This suggests the vector search is not working properly.")
        
        supabase.close()
        return results
    except Exception as e:
        print(f"❌ Error in similarity search: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_specific_query():
    """Test a specific query end-to-end"""
    print("\n" + "="*60)
    print("TEST 7: End-to-End Query Test")
    print("="*60)
    
    query = "Do you offer ongoing support and maintenance?"
    print(f"Query: '{query}'")
    
    try:
        from utils.assistant_rag import AssistantRAG
        assistant = AssistantRAG()
        
        # Test context retrieval
        context = assistant.retrieve_context(query)
        print(f"\n📊 Retrieved {len(context)} context chunks")
        
        if context:
            for i, chunk in enumerate(context, 1):
                print(f"\n--- Context {i} ---")
                print(f"Type: {chunk['chunk_type']}")
                print(f"Similarity: {chunk.get('similarity', 'N/A')}")
                print(f"Content: {chunk['text_content'][:200]}...")
        else:
            print("❌ No context retrieved!")
        
        return len(context) > 0
    except Exception as e:
        print(f"❌ Error in end-to-end test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "🔍" * 30)
    print("RAG DIAGNOSTIC TEST")
    print("🔍" * 30)
    
    # Run all tests
    db_ok = test_database_connection()
    if not db_ok:
        print("\n❌ Cannot connect to database. Check DATABASE_URL")
        return
    
    table_ok = test_table_exists()
    if not table_ok:
        print("\n❌ Table doesn't exist. Run the SQL migration first!")
        return
    
    count = test_data_count()
    if count == 0:
        print("\n❌ No data in table. Run: python -m utils.assistant_kb_loader")
        return
    
    test_sample_data()
    
    embedding = test_embedding_generation()
    if not embedding:
        print("\n❌ Cannot generate embeddings. Check OPENAI_API_KEY")
        return
    
    results = test_similarity_search(embedding)
    if not results:
        print("\n❌ Similarity search returned no results!")
        return
    
    test_specific_query()
    
    print("\n" + "="*60)
    print("DIAGNOSIS COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()

