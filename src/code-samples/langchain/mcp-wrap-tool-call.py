# :snippet-start: mcp-wrap-tool-call-py
from collections.abc import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.mcp import MCPAdapter
from langchain.messages import ToolMessage
from langchain.tools.tool_node import ToolCallRequest


@wrap_tool_call
def log_mcp_calls(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage],
) -> ToolMessage:
    """Intercept every tool call, MCP or otherwise, before and after it runs."""
    # Inspect or rewrite the request here; MCP provenance is on the tool's
    # metadata under `request.tool.metadata["mcp"]`.
    print(f"calling {request.tool_call['name']}")
    result = handler(request)
    print(f"-> {request.tool_call['name']} done")
    return result


async def agent_with_interception(target):
    async with MCPAdapter(target) as adapter:
        tools = await adapter.list_tools()
        return create_agent("claude-sonnet-4-6", tools, middleware=[log_mcp_calls])


# :snippet-end:


# :remove-start:
import asyncio
import warnings

from fastmcp import FastMCP
from langchain_core._api import LangChainBetaWarning

warnings.filterwarnings("ignore", category=LangChainBetaWarning)


def _server() -> FastMCP:
    mcp: FastMCP = FastMCP("weather")

    @mcp.tool
    def get_forecast(city: str) -> str:
        """Report the forecast for a city."""
        return f"{city}: 18C and clear."

    return mcp


async def _run() -> None:
    agent = await agent_with_interception(_server())
    assert agent is not None
    print("✓ mcp-wrap-tool-call validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
