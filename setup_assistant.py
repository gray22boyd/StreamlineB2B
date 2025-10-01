#!/usr/bin/env python3
"""
One-command setup script for the Streamline Assistant.
This script will:
1. Create database tables
2. Load the knowledge base
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Add utils to path
sys.path.append(os.path.dirname(__file__))

def check_env():
    """Check if required environment variables are set"""
    load_dotenv()
    
    required_vars = ['DATABASE_URL', 'OPENAI_API_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease add these to your .env file and try again.")
        return False
    
    print("✅ Environment variables found")
    return True


def create_tables():
    """Create database tables"""
    print("\n📦 Creating database tables...")
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # Read and execute migration
        with open('database/migrations/create_assistant_tables.sql', 'r') as f:
            sql = f.read()
            cur.execute(sql)
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Database tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


def load_knowledge_base():
    """Load knowledge base into database"""
    print("\n📚 Loading knowledge base...")
    
    try:
        from utils.assistant_kb_loader import main
        main()
        return True
        
    except Exception as e:
        print(f"❌ Error loading knowledge base: {e}")
        return False


def verify_setup():
    """Verify the setup was successful"""
    print("\n🔍 Verifying setup...")
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # Check if tables exist
        cur.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name IN ('assistant_knowledge_base', 'assistant_leads')
        """)
        table_count = cur.fetchone()[0]
        
        if table_count != 2:
            print("⚠️  Warning: Not all tables were created")
            return False
        
        # Check if knowledge base has data
        cur.execute("SELECT COUNT(*) FROM assistant_knowledge_base")
        chunk_count = cur.fetchone()[0]
        
        if chunk_count == 0:
            print("⚠️  Warning: Knowledge base is empty")
            return False
        
        cur.close()
        conn.close()
        
        print(f"✅ Setup verified! Knowledge base has {chunk_count} chunks")
        return True
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False


def main():
    print("=" * 60)
    print("🚀 Streamline Assistant Setup")
    print("=" * 60)
    
    # Step 1: Check environment
    if not check_env():
        sys.exit(1)
    
    # Step 2: Create tables
    if not create_tables():
        print("\n❌ Setup failed at table creation")
        sys.exit(1)
    
    # Step 3: Load knowledge base
    if not load_knowledge_base():
        print("\n❌ Setup failed at knowledge base loading")
        sys.exit(1)
    
    # Step 4: Verify
    if not verify_setup():
        print("\n⚠️  Setup completed with warnings")
        sys.exit(1)
    
    # Success!
    print("\n" + "=" * 60)
    print("✨ Setup Complete!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("   1. Start your Flask app: python frontend/app.py")
    print("   2. Visit your website")
    print("   3. Look for the purple chat button in the bottom right")
    print("   4. Ask: 'What does Streamline Automation do?'")
    print("\n🎉 Your AI Assistant is ready to help visitors!")


if __name__ == "__main__":
    main()

