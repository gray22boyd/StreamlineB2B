"""Agent registry for integrating multiple agent types without touching their code.

Currently registers only the marketing agent. Future agents can be added by
extending the REGISTRY map with their identifiers and adapters.
"""

from typing import Dict, Any, Callable
import os
import requests


class AgentAdapter:
    """Unified interface expected by the web app for any agent type."""

    def list_tools(self) -> list[Dict[str, Any]]:
        raise NotImplementedError

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class MarketingAgentAdapter(AgentAdapter):
    """Adapter that delegates to the marketing agent's call_tool and schemas."""

    def __init__(self) -> None:
        # Import locally to avoid side effects during Flask import time
        from agents.marketing_agent.mcp_server import call_tool as marketing_call_tool
        from agents.marketing_agent.schemas import MCP_TOOL_SCHEMAS, TOOL_DESCRIPTIONS
        self._call_tool_fn: Callable[[str, Dict[str, Any]], Dict[str, Any]] = marketing_call_tool
        self._schemas = MCP_TOOL_SCHEMAS
        self._descriptions = TOOL_DESCRIPTIONS

    def list_tools(self) -> list[Dict[str, Any]]:
        tools: list[Dict[str, Any]] = []
        for tool_name, input_schema in self._schemas.items():
            tools.append({
                "name": tool_name,
                "description": self._descriptions.get(tool_name, ""),
                "inputSchema": input_schema,
            })
        return tools

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_tool_fn(name, arguments)


class AnalyticsAgentAdapter(AgentAdapter):
    """Adapter for the analytics agent with natural language database querying."""

    def __init__(self) -> None:
        # Import locally to avoid side effects during Flask import time
        from agents.analytics_agent.mcp_server import call_analytics_tool
        from agents.analytics_agent.schemas import MCP_TOOL_SCHEMAS, TOOL_DESCRIPTIONS
        self._call_tool_fn: Callable[[str, Dict[str, Any]], Dict[str, Any]] = call_analytics_tool
        self._schemas = MCP_TOOL_SCHEMAS
        self._descriptions = TOOL_DESCRIPTIONS

    def list_tools(self) -> list[Dict[str, Any]]:
        tools: list[Dict[str, Any]] = []
        for tool_name, input_schema in self._schemas.items():
            tools.append({
                "name": tool_name,
                "description": self._descriptions.get(tool_name, ""),
                "inputSchema": input_schema,
            })
        return tools

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_tool_fn(name, arguments)


# Public registry mapping agent identifier -> adapter factory
def build_registry() -> Dict[str, AgentAdapter]:
    # Prefer remote MCP HTTP adapter when configured
    base_url = os.getenv('MCP_HTTP_BASE_URL')
    auth_token = os.getenv('MCP_AUTH_TOKEN')

    if base_url:
        class MarketingAgentHttpAdapter(AgentAdapter):
            def __init__(self, base_url: str, auth_token: str | None):
                self._base_url = base_url.rstrip('/')
                self._auth_token = auth_token

            def list_tools(self) -> list[Dict[str, Any]]:
                from agents.marketing_agent.schemas import MCP_TOOL_SCHEMAS, TOOL_DESCRIPTIONS
                return [
                    {
                        "name": name,
                        "description": TOOL_DESCRIPTIONS.get(name, ""),
                        "inputSchema": schema,
                    }
                    for name, schema in MCP_TOOL_SCHEMAS.items()
                ]

            def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
                payload = {"method": "tools/call", "params": {"name": name, "arguments": arguments}}
                headers = {"Content-Type": "application/json"}
                if self._auth_token:
                    headers["Authorization"] = f"Bearer {self._auth_token}"
                resp = requests.post(f"{self._base_url}/mcp", json=payload, headers=headers, timeout=30)
                resp.raise_for_status()
                body = resp.json()
                return body.get("result", body)

        return {
            "marketing": MarketingAgentHttpAdapter(base_url, auth_token),
        }

    # Fallback to in-process adapter
    return {
        "marketing": MarketingAgentAdapter(),
        "analytics": AnalyticsAgentAdapter(),
        # Future agents can be added here without changing existing routes
        # e.g., "customer_service": CustomerServiceAgentAdapter(),
    }



