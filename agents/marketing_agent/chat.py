#!/usr/bin/env python3
import requests
import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    import openai
except ImportError:
    print("OpenAI package required! Run: pip install openai")
    sys.exit(1)


class MarketingAgentChat:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.business_id = "cfbfa01d-6344-4823-b67a-ad0a702e7d61"

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("OPENAI_API_KEY required! Add it to your .env file")
            sys.exit(1)

        self.llm = openai.OpenAI(api_key=api_key)

    def call_tool(self, tool_name, arguments):
        payload = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        try:
            response = requests.post(f"{self.base_url}/mcp", json=payload, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def start(self):
        try:
            response = requests.get(self.base_url, timeout=2)
            if response.status_code != 200:
                print("MCP server not running. Start it with:")
                print("   python agents/marketing_agent/mcp_server.py")
                return
        except:
            print("MCP server not running. Start it with:")
            print("   python agents/marketing_agent/mcp_server.py")
            return

        print("INTERACTIVE LLM CHAT")
        print("=" * 50)
        print("Type 'quit' to exit\n")

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_pages",
                    "description": "List Facebook pages for the business",
                    "parameters": {
                        "type": "object",
                        "properties": {"business_id": {"type": "string"}},
                        "required": ["business_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "post_text",
                    "description": "Post text to Facebook",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "business_id": {"type": "string"},
                            "message": {"type": "string"}
                        },
                        "required": ["business_id", "message"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "post_image",
                    "description": "Post image with caption to Facebook",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "business_id": {"type": "string"},
                            "caption": {"type": "string"},
                            "image_url": {"type": "string"}
                        },
                        "required": ["business_id", "caption", "image_url"]
                    }
                }
            }
        ]

        messages = [
            {
                "role": "system",
                "content": f"You are a helpful marketing assistant for business ID {self.business_id}. You can manage Facebook pages using the available tools. When users ask you to post something, use the tools to actually do it."
            }
        ]

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ['quit', 'exit']:
                    break

                if not user_input:
                    continue

                messages.append({"role": "user", "content": user_input})

                response = self.llm.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    tools=tools,
                    tool_choice="auto"
                )

                message = response.choices[0].message

                if message.content:
                    print(f"AI: {message.content}")

                if message.tool_calls:
                    tool_results = []
                    for tool_call in message.tool_calls:
                        print(f"Using {tool_call.function.name}...")
                        args = json.loads(tool_call.function.arguments)
                        result = self.call_tool(tool_call.function.name, args)

                        if 'error' in result:
                            print(f"Error: {result['error']}")
                            tool_results.append(f"Error: {result['error']}")
                        elif 'result' in result and result['result'].get('success'):
                            # Show actual results based on tool type
                            if tool_call.function.name == 'list_pages':
                                pages = result['result'].get('pages', [])
                                print(f"Found {len(pages)} page(s):")
                                for page in pages:
                                    print(f"  - {page['name']} (ID: {page['id']}) - {page['category']}")
                                    print(f"    Followers: {page['followers']}, Likes: {page['likes']}")
                                tool_results.append(json.dumps(result['result']))
                            elif tool_call.function.name == 'post_text':
                                print(f"Posted successfully: {result['result'].get('message', 'Text posted!')}")
                                tool_results.append("Post created successfully")
                            elif tool_call.function.name == 'post_image':
                                print(f"Posted successfully: {result['result'].get('message', 'Image posted!')}")
                                tool_results.append("Image post created successfully")
                            else:
                                print(f"Success: {result['result']}")
                                tool_results.append(json.dumps(result['result']))
                        else:
                            print(f"Unexpected result: {result}")
                            tool_results.append(f"Unexpected result: {result}")

                    messages.append({
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": message.tool_calls
                    })

                    for i, tool_call in enumerate(message.tool_calls):
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_results[i]
                        })
                else:
                    messages.append({"role": "assistant", "content": message.content})

            except KeyboardInterrupt:
                break


def main():
    chat = MarketingAgentChat()
    chat.start()


if __name__ == "__main__":
    main()