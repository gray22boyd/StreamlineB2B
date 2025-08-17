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
    from tools import FacebookMarketingTools

    logger.info("Successfully imported FacebookMarketingTools")
except ImportError as e:
    logger.error(f"Failed to import FacebookMarketingTools: {e}")
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
    """Call the marketing tools"""
    logger.info(f"Calling tool: {tool_name} with args: {arguments}")

    business_id = arguments.get("business_id")
    if not business_id:
        logger.error("business_id is required")
        return {"error": "business_id is required"}

    try:
        tools = FacebookMarketingTools(business_id)
        logger.info(f"Created FacebookMarketingTools for business: {business_id}")
    except Exception as e:
        logger.error(f"Failed to create FacebookMarketingTools: {e}")
        return {"error": f"Failed to initialize tools: {str(e)}"}

    if tool_name == "list_pages":
        return tools.list_pages()
    elif tool_name == "post_text":
        message = arguments.get("message")
        if not message:
            return {"error": "message is required for post_text"}
        return tools.post_text(message)
    elif tool_name == "post_image":
        caption = arguments.get("caption")
        image_url = arguments.get("image_url")
        if not caption or not image_url:
            return {"error": "caption and image_url are required for post_image"}
        return tools.post_image(caption, image_url)
    else:
        return {"error": f"Unknown tool '{tool_name}'"}


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
    logger.info("🚀 Starting Marketing Agent MCP Server (HTTP mode)...")
    logger.info("📱 Available tools: list_pages, post_text, post_image")
    logger.info("🔗 Server running on http://localhost:8000")
    logger.info("📋 Send POST requests to /mcp endpoint")
    server.serve_forever()


# ---------- stdio server mode ----------
async def run_stdio_server():
    logger.info("Starting stdio server mode")

    if Server is None:
        logger.error("MCP stdio server requires the `mcp` Python package.")
        sys.exit(1)

    server = Server("facebook-marketing")

    @server.list_tools()
    async def list_tools():
        logger.info("list_tools() called")
        tools = [
            Tool(
                name="list_pages",
                description="List all Facebook pages that the business has access to manage",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "business_id": {"type": "string"}
                    },
                    "required": ["business_id"]
                }
            ),
            Tool(
                name="post_text",
                description="Create a text post on the business's Facebook page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "business_id": {"type": "string"},
                        "message": {"type": "string"}
                    },
                    "required": ["business_id", "message"]
                }
            ),
            Tool(
                name="post_image",
                description="Create an image post with caption on the business's Facebook page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "business_id": {"type": "string"},
                        "caption": {"type": "string"},
                        "image_url": {"type": "string"}
                    },
                    "required": ["business_id", "caption", "image_url"]
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