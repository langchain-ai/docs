# :snippet-start: mcp-client-group-py
from fastmcp.client import Client
from fastmcp.client.group import ClientGroup
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter


async def agent_from_group(legacy_url: str, modern_url: str):
    # One connection per server: a `ClientGroup` keeps each server on its own
    # negotiated protocol era, so a legacy and a modern server run side by side.
    # It also namespaces every tool as `{server}_{tool}`, so two servers exposing
    # the same tool name stay distinct.
    group = ClientGroup(
        {
            "weather": Client(legacy_url, mode="legacy"),
            "calc": Client(modern_url, mode="auto"),
        }
    )
    async with MCPAdapter(group) as adapter:
        tools = await adapter.list_tools()
        return create_agent("claude-sonnet-4-6", tools)


# :snippet-end:


# :remove-start:
import asyncio
import warnings

from fastmcp import FastMCP
from langchain_core._api import LangChainBetaWarning

warnings.filterwarnings("ignore", category=LangChainBetaWarning)


def _server(name: str) -> FastMCP:
    mcp: FastMCP = FastMCP(name)

    @mcp.tool
    def get_data() -> str:
        """A tool whose name is shared across both servers."""
        return f"{name}-data"

    return mcp


async def _run() -> None:
    group = ClientGroup(
        {
            "weather": Client(_server("weather"), mode="legacy"),
            "calc": Client(_server("calc"), mode="auto"),
        }
    )
    async with MCPAdapter(group) as adapter:
        tools = await adapter.list_tools()
    # Same upstream tool name, kept distinct by the server prefix.
    assert sorted(t.name for t in tools) == ["calc_get_data", "weather_get_data"]
    print("✓ mcp-client-group validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
