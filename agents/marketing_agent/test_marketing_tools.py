# test_marketing_tools.py
import os
import psycopg2
from dotenv import load_dotenv
from agents.marketing_agent.tools import FacebookMarketingTools

load_dotenv()


def test_marketing_tools():
    try:
        # First, get Legends Golf's business ID from database
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()

        cur.execute("SELECT id FROM businesses WHERE email = 'grayson@streamlineautomationco.com'")
        result = cur.fetchone()

        if not result:
            print("❌ Legends Golf business not found!")
            return

        business_id = result[0]
        print(f"✅ Found Legends Golf business: {business_id}")

        # Create marketing tools for Legends Golf
        print("\n🔧 Creating marketing tools...")
        marketing_tools = FacebookMarketingTools(business_id)

        print(f"✅ Tools created successfully!")
        print(f"   Page ID: {marketing_tools.page_id}")
        print(f"   Page Name: {marketing_tools.page_name}")
        print(f"   Token (first 20 chars): {marketing_tools.access_token[:20]}...")

        # Test list_pages function
        print("\n📋 Testing list_pages()...")
        result = marketing_tools.list_pages()

        if result['success']:
            print(f"✅ list_pages() successful!")
            print(f"   Found {result['count']} pages:")
            for page in result['pages']:
                print(f"   - {page['name']} (ID: {page['id']}) - {page['category']}")
        else:
            print(f"❌ list_pages() failed:")
            print(f"   Error: {result['error']}")
            if 'response' in result:
                print(f"   Response: {result['response']}")

        # Test post_text function
        print("\n📝 Testing post_text()...")
        post_result = marketing_tools.post_text("Hello from my AI marketing agent! 🤖 Testing from Legends Golf.")

        if post_result['success']:
            print(f"✅ post_text() successful!")
            print(f"   Post ID: {post_result['post_id']}")
            print(f"   Message: {post_result['message']}")
            print(f"   Posted to: {post_result['page_name']}")
        else:
            print(f"❌ post_text() failed:")
            print(f"   Error: {post_result['error']}")

        # Test post_image function
        print("\n🖼️ Testing post_image()...")
        image_result = marketing_tools.post_image(
            caption="Testing image post from my AI marketing agent! 📸",
            image_url="https://picsum.photos/800/600?random=1"
        )

        if image_result['success']:
            print(f"✅ post_image() successful!")
            print(f"   Post ID: {image_result['post_id']}")
            print(f"   Message: {image_result['message']}")
            print(f"   Image URL: {image_result['image_url']}")
        else:
            print(f"❌ post_image() failed:")
            print(f"   Error: {image_result['error']}")

        cur.close()
        conn.close()


        # Test list_recent_posts function
        print("\n📋 Testing list_recent_posts()...")
        recent_posts_result = marketing_tools.list_recent_posts(limit=5)

        if recent_posts_result['success']:
            print(f"✅ list_recent_posts() successful!")
            print(f"   {recent_posts_result['summary']}")
            print(f"   Recent posts:")
            for i, post in enumerate(recent_posts_result['posts'], 1):
                print(f"     {i}. {post['preview']} (Created: {post['created_time']})")
        else:
            print(f"❌ list_recent_posts() failed:")
            print(f"   Error: {recent_posts_result['error']}")

    except Exception as e:
        print(f"❌ Test failed: {e}")



if __name__ == "__main__":
    test_marketing_tools()