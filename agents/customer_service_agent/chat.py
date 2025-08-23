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


class CustomerServiceAgentChat:
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
                print("   python agents/customer_service_agent/mcp_server.py")
                return
        except:
            print("MCP server not running. Start it with:")
            print("   python agents/customer_service_agent/mcp_server.py")
            return

        print("CUSTOMER SERVICE AGENT CHAT")
        print("=" * 50)
        print("Type 'quit' to exit")
        print("I can help you with customer service queries using our knowledge base.\n")

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "pull_tables_from_db",
                    "description": "Get a list of available customer service tables in the database",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pull_relevant_chunks",
                    "description": "Search for relevant information in the customer service knowledge base",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The customer's question or query"
                            },
                            "table_name": {
                                "type": "string",
                                "description": "The table name to search in (e.g., 'customer_service_embeddings')"
                            }
                        },
                        "required": ["query", "table_name"]
                    }
                }
            }
        ]

        messages = [
            {
                "role": "system",
                "content": f"You are a helpful customer service assistant for business ID {self.business_id}. You can search through customer service knowledge bases and provide accurate information to customers. When customers ask questions, use the available tools to find relevant information from the database. Always be polite, professional, and helpful. If you don't find relevant information, let the customer know and offer to escalate their inquiry."
            }
        ]

        while True:
            try:
                user_input = input("Customer: ").strip()

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
                    print(f"Agent: {message.content}")

                if message.tool_calls:
                    tool_results = []
                    for tool_call in message.tool_calls:
                        print(f"Searching knowledge base...")
                        args = json.loads(tool_call.function.arguments)
                        result = self.call_tool(tool_call.function.name, args)

                        if 'error' in result:
                            print(f"Error: {result['error']}")
                            tool_results.append(f"Error: {result['error']}")
                        elif 'result' in result and result['result'].get('success'):
                            # Show actual results based on tool type
                            if tool_call.function.name == 'pull_tables_from_db':
                                tables = result['result'].get('tables', [])
                                print(f"Found {len(tables)} available knowledge base(s):")
                                for table_row in tables:
                                    table_name = table_row['table_name']
                                    print(f"  - {table_name}")
                                tool_results.append(json.dumps(result['result']))
                            elif tool_call.function.name == 'pull_relevant_chunks':
                                relevant_info = result['result'].get('relevant_chunks', '')
                                print(f"Found relevant information:")
                                print(f"  {relevant_info[:200]}...")
                                tool_results.append(relevant_info)
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
    chat = CustomerServiceAgentChat()
    chat.start()


if __name__ == "__main__":
    main()