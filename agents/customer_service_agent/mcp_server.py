import sys
import os
import json
import logging
from typing import Any, Dict
from http.server import HTTPServer, BaseHTTPRequestHandler

# Set up logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Add current directory to path so imports work in stdio mode
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger.info(f"Starting MCP Server from: {os.path.abspath(__file__)}")
logger.info(f"Python path: {sys.path}")
logger.info(f"Working directory: {os.getcwd()}")

try:
    from tools import CustomerServiceTools

    logger.info("Successfully imported CustomerServiceTools")
except ImportError as e:
    logger.error(f"Failed to import CustomerServiceTools: {e}")
    sys.exit(1)

# ---------- MCP stdio imports ----------
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool

    # ToolCall might not be available in all MCP versions
    try:
        from mcp.types import ToolCall
    except ImportError:
        ToolCall = None
    logger.info("Successfully imported MCP modules")
except ImportError as e:
    logger.error(f"MCP package not installed: {e}")
    Server = None  # stdio mode won't work if MCP package isn't installed


# ---------- Shared logic ----------
def call_tool(tool_name: str, arguments: Dict[str, Any]):
    """Call the customer service tools"""
    logger.info(f"Calling tool: {tool_name} with args: {arguments}")

    try:
        tools = CustomerServiceTools(schema = "Legends")
        if tool_name == "pull_tables_from_db":
            result = tools.pull_tables_from_db()
            logger.info(f"pull_tables_from_db result: {result}")
            return {"tables": result}
        elif tool_name == "pull_relevant_chunks":
            query = arguments.get("query")
            table_name = arguments.get("table_name")
            if not query:
                return {"error": "query is required for pull_relevant_chunks"}
            if not table_name:
                return {"error": "table_name is required for pull_relevant_chunks"}
            result = tools.pull_relevant_chunks(query, table_name)
            logger.info(f"pull_relevant_chunks result: {result}")
            return {"text": result}
        else:
            return {"error": f"Unknown tool '{tool_name}'"}
    except Exception as e:
        logger.error(f"Tool call failed: {e}")
        return {"error": f"Tool call failed: {str(e)}"}


# ---------- HTTP server mode ----------
class MCPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Simple health check
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"MCP Server running")

    def do_POST(self):
        if self.path == '/mcp':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))

                if request_data.get('method') == 'tools/call':
                    params = request_data.get('params', {})
                    tool_name = params.get('name')
                    arguments = params.get('arguments', {})

                    result = call_tool(tool_name, arguments)

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"result": result}).encode('utf-8'))
                else:
                    self.send_response(400)
                    self.end_headers()
            except Exception as e:
                logger.error(f"HTTP handler error: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


def run_http_server():
    server = HTTPServer(('localhost', 8000), MCPHandler)
    logger.info("Starting Customer Service Agent MCP Server (HTTP mode)...")
    logger.info("Available tools: pull_tables_from_db, pull_relevant_chunks")
    logger.info("Server running on http://localhost:8000")
    logger.info("Send POST requests to /mcp endpoint")
    server.serve_forever()


# ---------- stdio server mode ----------
async def run_stdio_server():
    logger.info("Starting stdio server mode")

    if Server is None:
        logger.error("MCP stdio server requires the `mcp` Python package.")
        sys.exit(1)

    server = Server("customer-service")

    @server.list_tools()
    async def list_tools():
        logger.info("list_tools() called")
        tools = [
            Tool(
                name="pull_tables_from_db",
                description="Pull a list of tables from the supabase database that are for public facing use",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="pull_relevant_chunks",
                description="Pull relevant chunks from the business's database for a given query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "table_name": {"type": "string"}
                    },
                    "required": ["query", "table_name"]
                }
            )
        ]
        logger.info(f"Returning {len(tools)} tools")
        return tools

    @server.call_tool()
    async def handle_tool_call(name: str, arguments: Dict[str, Any]):
        logger.info(f"handle_tool_call: {name} with {arguments}")
        result = call_tool(name, arguments)
        logger.info(f"Tool call result: {result}")
        return result

    logger.info("Setting up stdio server...")
    async with stdio_server() as streams:
        logger.info("stdio server running...")
        # Handle different MCP versions and stream formats
        if len(streams) == 2:
            read, write = streams
            try:
                await server.run(read, write, {})  # Newer MCP version
            except TypeError:
                try:
                    await server.run(read, write)  # Older MCP version
                except Exception as e:
                    logger.error(f"Server run failed: {e}")
                    raise
        else:
            logger.error(f"Unexpected stdio_server format: {streams}")
            raise ValueError("Unexpected stdio_server stream format")


# ---------- Entry ----------
if __name__ == "__main__":
    logger.info(f"Script started with args: {sys.argv}")

    if "--stdio" in sys.argv:
        logger.info("Running in stdio mode")
        import asyncio

        asyncio.run(run_stdio_server())
    else:
        logger.info("Running in HTTP mode")
        run_http_server()