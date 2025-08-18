# test_mcp_server.py
import requests
import json


def test_mcp_server():
    base_url = "http://localhost:8000"

    print("🧪 Testing Marketing Agent MCP Server...")

    # Test list_pages tool
    print("\n📋 Testing list_pages tool...")
    payload = {
        "method": "tools/call",
        "params": {
            "name": "list_pages",
            "arguments": {
                "business_id": "cfbfa01d-6344-4823-b67a-ad0a702e7d61"  # Your Legends Golf ID
            }
        }
    }

    try:
        response = requests.post(f"{base_url}/mcp", json=payload)
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test post_text tool
    print("\n📝 Testing post_text tool...")
    payload = {
        "method": "tools/call",
        "params": {
            "name": "post_text",
            "arguments": {
                "business_id": "cfbfa01d-6344-4823-b67a-ad0a702e7d61",
                "message": "Hello from MCP server! 🤖 This post was created through the MCP protocol."
            }
        }
    }

    try:
        response = requests.post(f"{base_url}/mcp", json=payload)
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_mcp_server()