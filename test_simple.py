import os
import sys
sys.path.append('frontend')

# Set database URL 
os.environ['DATABASE_URL'] = 'postgresql://postgres.fflamjmanktqkckhdacp:WillyWonka22!at-aws-0-us-east-2.pooler.supabase.com:6543/postgres'.replace('at-', '@')

try:
    from business_agent_manager import create_business_agent_manager
    manager = create_business_agent_manager('cfbfa01d-6344-4823-b67a-ad0a702e7d61', None)
    
    response = manager.process_message('marketing', 'please list pages', None)
    print('Response type:', type(response))
    print('Response success:', response.get('success') if isinstance(response, dict) else 'Not a dict')
    if isinstance(response, dict) and not response.get('success'):
        print('Error:', response.get('error'))
    
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()
