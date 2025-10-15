#!/usr/bin/env python3
# agents/analytics_agent/mcp_server.py
"""
MCP HTTP Server for Analytics Agent
Provides HTTP interface for the analytics agent tools
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any
from dotenv import load_dotenv

from agents.analytics_agent.tools import AnalyticsTools
from agents.analytics_agent.schemas import MCP_TOOL_SCHEMAS, TOOL_DESCRIPTIONS

load_dotenv()


class AnalyticsMCPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for analytics agent MCP server"""
    
    def _set_headers(self, status_code=200, content_type='application/json'):
        """Set HTTP response headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def _check_auth(self):
        """Check authorization token if configured"""
        auth_token = os.getenv('MCP_AUTH_TOKEN')
        if not auth_token:
            return True  # No auth required if token not set
        
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        
        token = auth_header.replace('Bearer ', '')
        return token == auth_token
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self._set_headers(204)
    
    def do_GET(self):
        """Handle GET requests - serve MCP metadata"""
        if not self._check_auth():
            self._set_headers(401)
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
            return
        
        if self.path == '/health':
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "healthy", "agent": "analytics"}).encode())
            return
        
        if self.path == '/mcp' or self.path == '/mcp/tools':
            # Return list of available tools
            tools = [
                {
                    "name": name,
                    "description": TOOL_DESCRIPTIONS.get(name, ""),
                    "inputSchema": schema
                }
                for name, schema in MCP_TOOL_SCHEMAS.items()
            ]
            
            self._set_headers(200)
            self.wfile.write(json.dumps({"tools": tools}).encode())
            return
        
        # 404 for unknown paths
        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        """Handle POST requests - execute tool calls"""
        if not self._check_auth():
            self._set_headers(401)
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
            return
        
        if self.path != '/mcp':
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
            return
        
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode('utf-8'))
            
            # Extract method and params
            method = request_data.get('method')
            params = request_data.get('params', {})
            
            if method == 'tools/call':
                # Execute tool call
                tool_name = params.get('name')
                arguments = params.get('arguments', {})
                
                result = call_analytics_tool(tool_name, arguments)
                
                self._set_headers(200)
                self.wfile.write(json.dumps({"result": result}).encode())
                return
            
            elif method == 'tools/list':
                # Return tool list
                tools = [
                    {
                        "name": name,
                        "description": TOOL_DESCRIPTIONS.get(name, ""),
                        "inputSchema": schema
                    }
                    for name, schema in MCP_TOOL_SCHEMAS.items()
                ]
                
                self._set_headers(200)
                self.wfile.write(json.dumps({"result": {"tools": tools}}).encode())
                return
            
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": f"Unknown method: {method}"}).encode())
                return
        
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
        
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[Analytics MCP] {self.address_string()} - {format % args}")


def call_analytics_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call an analytics tool with given arguments
    
    Args:
        tool_name: Name of the tool to call
        arguments: Dictionary of arguments for the tool
        
    Returns:
        Result dictionary from the tool
    """
    try:
        # Create analytics tools instance
        # In production, you might want to pass business_id from arguments
        business_id = arguments.get('business_id')
        tools = AnalyticsTools(business_id=business_id)
        
        # Route to appropriate tool
        if tool_name == 'query_database':
            question = arguments.get('question')
            if not question:
                return {"success": False, "error": "Missing required argument: question"}
            return tools.query_database(question)
        
        elif tool_name == 'get_quick_stats':
            return tools.get_quick_stats()
        
        elif tool_name == 'get_top_products':
            limit = arguments.get('limit', 10)
            return tools.get_top_products(limit)
        
        elif tool_name == 'get_customer_insights':
            customer_id = arguments.get('customer_id')
            return tools.get_customer_insights(customer_id)
        
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Tool execution error: {str(e)}"
        }


def run_server(host='0.0.0.0', port=8020):
    """
    Start the analytics MCP HTTP server
    
    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to listen on (default: 8020)
    """
    server_address = (host, port)
    httpd = HTTPServer(server_address, AnalyticsMCPHandler)
    
    print(f"🚀 Analytics MCP Server starting on {host}:{port}")
    print(f"📊 Analytics Agent ready for business insights")
    
    auth_token = os.getenv('MCP_AUTH_TOKEN')
    if auth_token:
        print(f"🔒 Authentication enabled")
    else:
        print(f"⚠️  Warning: No authentication token set (MCP_AUTH_TOKEN)")
    
    print(f"\nAvailable endpoints:")
    print(f"  GET  /health - Health check")
    print(f"  GET  /mcp/tools - List available tools")
    print(f"  POST /mcp - Execute tool calls")
    print(f"\nPress Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n\n👋 Shutting down Analytics MCP Server...")
        httpd.shutdown()


if __name__ == '__main__':
    # Get host and port from environment or use defaults
    host = os.getenv('MCP_HOST', '0.0.0.0')
    port = int(os.getenv('MCP_PORT', '8020'))
    
    run_server(host, port)



