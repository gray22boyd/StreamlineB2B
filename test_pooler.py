#!/usr/bin/env python3
import psycopg2

# Test the new pooler connection
pooler_url = 'postgresql://postgres.fflamjmanktqkckhdacp:WillyWonka22!@aws-0-us-east-2.pooler.supabase.com:6543/postgres'
print('Testing pooler connection...')
print(f'Connection string: {pooler_url}')

try:
    conn = psycopg2.connect(pooler_url)
    cur = conn.cursor()
    cur.execute('SELECT version()')
    result = cur.fetchone()
    print('✅ Pooler connection successful!')
    print(f'Database version: {result[0][:50]}...')
    
    # Test a simple query
    cur.execute('SELECT COUNT(*) FROM users')
    user_count = cur.fetchone()[0]
    print(f'✅ Users table accessible, found {user_count} users')
    
    cur.close()
    conn.close()
except Exception as e:
    print(f'❌ Pooler connection failed: {e}')
    import traceback
    traceback.print_exc()
