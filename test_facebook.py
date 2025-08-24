import os
import sys
sys.path.append('frontend')
sys.path.append('agents')

# Set database URL 
os.environ['DATABASE_URL'] = 'postgresql://postgres.fflamjmanktqkckhdacp:WillyWonka22!at-aws-0-us-east-2.pooler.supabase.com:6543/postgres'.replace('at-', '@')

from agents.marketing_agent.tools import FacebookMarketingTools

# Test what the Facebook agent actually returns
try:
    agent = FacebookMarketingTools('cfbfa01d-6344-4823-b67a-ad0a702e7d61')
    print("✅ Agent created successfully")
    
    result = agent.list_pages()
    print('Result type:', type(result))
    print('Result:', result)
    
    # Check if result contains a list that might be causing issues
    if isinstance(result, dict) and 'pages' in result:
        print('Pages type:', type(result['pages']))
        print('Pages value:', result['pages'])
        
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()
