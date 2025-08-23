# test_customer_service_tools.py
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import the tools
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools import CustomerServiceTools

load_dotenv()


def test_customer_service_tools():
    try:
        print("🔧 Testing Customer Service Tools...")
        print("=" * 50)

        # Test pull_tables_from_db function
        print("\n📋 Testing pull_tables_from_db()...")
        try:
            tools = CustomerServiceTools(schema = "Legends")
            tables_result = tools.pull_tables_from_db()
            print(f"✅ pull_tables_from_db() successful!")
            print(f"   Found {len(tables_result)} tables:")
            for table_row in tables_result:
                table_name = table_row['table_name']
                print(f"   - {table_name}")
        except Exception as e:
            print(f"❌ pull_tables_from_db() failed:")
            print(f"   Error: {e}")

        # Test pull_relevant_chunks function
        print("\n🔍 Testing pull_relevant_chunks()...")
        try:
            # Test with a sample query and table
            query = "What is the total distance of the course?"
            table_name = "customer_service_embeddings"
            
            chunks_result = tools.pull_relevant_chunks(query, table_name)
            print(f"✅ pull_relevant_chunks() successful!")
            print(f"   Query: '{query}'")
            print(f"   Table: '{table_name}'")
            print(f"   Result: {chunks_result[:200]}...")  # Show first 200 chars
        except Exception as e:
            print(f"❌ pull_relevant_chunks() failed:")
            print(f"   Error: {e}")

        # Test with different query
        print("\n🔍 Testing pull_relevant_chunks() with different query...")
        try:
            query2 = "What are the course rules?"
            chunks_result2 = tools.pull_relevant_chunks(query2, table_name)
            print(f"✅ pull_relevant_chunks() successful!")
            print(f"   Query: '{query2}'")
            print(f"   Table: '{table_name}'")
            print(f"   Result: {chunks_result2[:200]}...")  # Show first 200 chars
        except Exception as e:
            print(f"❌ pull_relevant_chunks() failed:")
            print(f"   Error: {e}")

        print("\n" + "=" * 50)
        print("🎉 Customer Service Tools testing completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_customer_service_tools()