#!/usr/bin/env python3
"""
Test script to verify the updated authentication system works with Supabase UUID schema
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path so we can import from frontend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frontend.app import create_user, get_user_by_email, verify_password, get_db_connection

load_dotenv()

def test_database_connection():
    """Test basic database connection"""
    print("🔌 Testing database connection...")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"✅ Connected to Supabase!")
        print(f"📊 PostgreSQL version: {version['version'][:50]}...")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_table_structure():
    """Test that required tables exist with correct structure"""
    print("\n📋 Testing table structure...")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if users table exists with correct columns
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        users_columns = cur.fetchall()
        
        if users_columns:
            print("✅ Users table found with columns:")
            for col in users_columns:
                print(f"   - {col['column_name']}: {col['data_type']}")
        else:
            print("❌ Users table not found!")
            return False
            
        # Check user_agents table
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user_agents' AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        user_agents_columns = cur.fetchall()
        
        if user_agents_columns:
            print("✅ User_agents table found with columns:")
            for col in user_agents_columns:
                print(f"   - {col['column_name']}: {col['data_type']}")
        else:
            print("❌ User_agents table not found!")
            return False
            
        # Check businesses table
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'businesses' AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        businesses_columns = cur.fetchall()
        
        if businesses_columns:
            print("✅ Businesses table found with columns:")
            for col in businesses_columns:
                print(f"   - {col['column_name']}: {col['data_type']}")
        else:
            print("❌ Businesses table not found!")
            return False
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Table structure test failed: {e}")
        return False

def get_test_business_id():
    """Get a business ID for testing"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id, name FROM businesses LIMIT 1")
        business = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if business:
            print(f"📍 Using business: {business['name']} (ID: {business['id']})")
            return str(business['id'])
        else:
            print("❌ No active businesses found!")
            return None
    except Exception as e:
        print(f"❌ Failed to get business ID: {e}")
        return None

def test_user_creation():
    """Test creating a new user"""
    print("\n👤 Testing user creation...")
    
    business_id = get_test_business_id()
    if not business_id:
        return False
    
    test_email = "test_user@streamlineautomationco.com"
    test_password = "testpass123"
    test_name = "Test User"
    
    try:
        # Try to create user
        success = create_user(test_email, test_password, test_name, business_id)
        
        if success:
            print(f"✅ User created successfully: {test_email}")
            return test_email, test_password
        else:
            print(f"⚠️  User creation returned False (user might already exist)")
            return test_email, test_password  # Still return for login test
            
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        return None, None

def test_user_login(email, password):
    """Test user login functionality"""
    print("\n🔐 Testing user login...")
    
    if not email or not password:
        print("❌ No email/password provided for login test")
        return False
    
    try:
        # Get user by email
        user = get_user_by_email(email)
        
        if user:
            print(f"✅ User found: {user['name']}")
            print(f"📧 Email: {user['email']}")
            print(f"🏢 Business: {user['business_name']}")
            print(f"🎭 Role: {user['role']}")
            print(f"🤖 Agents: {user['agents']}")
            
            # Test password verification
            if verify_password(password, user['password_hash']):
                print("✅ Password verification successful")
                return True
            else:
                print("❌ Password verification failed")
                return False
        else:
            print(f"❌ User not found: {email}")
            return False
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

def test_business_list():
    """Test getting business list for registration dropdown"""
    print("\n🏢 Testing business list for registration...")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id, name FROM businesses ORDER BY name")
        businesses = cur.fetchall()
        
        if businesses:
            print(f"✅ Found {len(businesses)} active businesses:")
            for business in businesses:
                print(f"   - {business['name']} (ID: {business['id']})")
        else:
            print("❌ No active businesses found!")
            return False
            
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Business list test failed: {e}")
        return False

def cleanup_test_user():
    """Clean up test user if needed"""
    print("\n🧹 Cleaning up test data...")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Delete test user (will cascade to user_agents)
        cur.execute("DELETE FROM users WHERE email = %s", ("test_user@streamlineautomationco.com",))
        deleted_count = cur.rowcount
        
        conn.commit()
        cur.close()
        conn.close()
        
        if deleted_count > 0:
            print(f"✅ Cleaned up {deleted_count} test user(s)")
        else:
            print("ℹ️  No test users to clean up")
            
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

def main():
    """Run all authentication tests"""
    print("🧪 StreamlineB2B Authentication System Test")
    print("=" * 50)
    
    # Test 1: Database connection
    if not test_database_connection():
        print("❌ Database connection failed - stopping tests")
        return
    
    # Test 2: Table structure
    if not test_table_structure():
        print("❌ Table structure issues - stopping tests")
        return
    
    # Test 3: Business list
    if not test_business_list():
        print("❌ Business list issues - stopping tests")
        return
    
    # Test 4: User creation
    email, password = test_user_creation()
    
    # Test 5: User login
    if email and password:
        test_user_login(email, password)
    
    # Test 6: Cleanup
    cleanup_test_user()
    
    print("\n🎯 Authentication system tests completed!")
    print("💡 If all tests passed, your login system should work properly.")

if __name__ == "__main__":
    main()
