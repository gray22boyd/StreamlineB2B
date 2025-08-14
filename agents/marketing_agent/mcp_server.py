# agents/marketing_agent/mcp_server.py

import asyncio
import json
from typing import Any, Dict, List
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tools import FacebookMarketingTools

# Simple HTTP server for MCP
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading


class MCPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/mcp':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))

                # Handle MCP tool calls
                if request_data.get('method') == 'tools/call':
                    params = request_data.get('params', {})
                    tool_name = params.get('name')
                    arguments = params.get('arguments', {})

                    result = self.call_tool(tool_name, arguments)

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode('utf-8'))
                else:
                    self.send_response(400)
                    self.end_headers()

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {"error": str(e)}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Call the marketing tools"""
        try:
            business_id = arguments.get("business_id")
            if not business_id:
                return {"error": "business_id is required"}

            # Create marketing tools for this business
            tools = FacebookMarketingTools(business_id)

            if tool_name == "list_pages":
                result = tools.list_pages()
            elif tool_name == "post_text":
                message = arguments.get("message")
                if not message:
                    return {"error": "message is required for post_text"}
                result = tools.post_text(message)
            elif tool_name == "post_image":
                caption = arguments.get("caption")
                image_url = arguments.get("image_url")
                if not caption or not image_url:
                    return {"error": "caption and image_url are required for post_image"}
                result = tools.post_image(caption, image_url)
            else:
                return {"error": f"Unknown tool '{tool_name}'"}

            return {"result": result}

        except Exception as e:
            return {"error": str(e)}


def run_server():
    """Run the MCP server"""
    server = HTTPServer(('localhost', 8000), MCPHandler)
    print("🚀 Starting Marketing Agent MCP Server...")
    print("📱 Available tools: list_pages, post_text, post_image")
    print("🔗 Server running on http://localhost:8000")
    print("📋 Send POST requests to /mcp endpoint")
    server.serve_forever()


if __name__ == "__main__":
    run_server()