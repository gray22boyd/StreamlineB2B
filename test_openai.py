import os
import sys
sys.path.append('frontend')

# Set environment variables like Railway would
os.environ['DATABASE_URL'] = 'postgresql://postgres.fflamjmanktqkckhdacp:WillyWonka22!@aws-0-us-east-2.pooler.supabase.com:6543/postgres'
os.environ['OPENAI_API_KEY'] = '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'

print("Testing OpenAI integration locally...")

try:
    from business_agent_manager import create_business_agent_manager
    print("✅ Manager import successful")
    
    manager = create_business_agent_manager('cfbfa01d-6344-4823-b67a-ad0a702e7d61', None)
    print(f"✅ Manager created, OpenAI client: {manager.openai_client is not None}")
    
    agent = manager.get_agent_instance('marketing')
    print("✅ Marketing agent created")
    
    # Test the actual issue - simulate what happens in chat
    response = manager.process_message('marketing', 'please list pages', None)
    print(f"✅ Process message result: {response[:100]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
