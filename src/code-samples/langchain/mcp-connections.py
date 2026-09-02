# :snippet-start: mcp-lifecycle-short-py
from langchain.mcp import MCPAdapter


async def load_tools(target) -> list:
    # Discover once inside a short-lived context. The tools hold the client, so
    # they stay callable after the context exits — there is no need to keep the
    # adapter open for the life of the agent.
    async with MCPAdapter(target) as adapter:
        return await adapter.list_tools()


# :snippet-end:


# :snippet-start: mcp-graph-factory-py
from langchain.agents import create_agent

SERVERS = {
    "weather": "http://localhost:8001/mcp",
    "calc": "http://localhost:8002/mcp",
}


async def make_graph():
    """Build an agent over an MCP fleet. Called once per run by `langgraph dev`."""
    config = {"mcpServers": {name: {"url": url} for name, url in SERVERS.items()}}
    # A long-lived deployment discovers per run, but reuses one HTTP connection
    # pool underneath. `cache_mode="use"` serves a cached tool list within the
    # server's TTL instead of re-listing on every run.
    async with MCPAdapter(config) as adapter:
        tools = await adapter.list_tools(cache_mode="use")
    return create_agent("claude-sonnet-4-6", tools)


# :snippet-end:


# :snippet-start: mcp-protocol-eras-py
from fastmcp.client import Client


async def load_across_eras(legacy_target, modern_target) -> list:
    # MCP has two protocol eras. FastMCP negotiates per connection, so a
    # separate adapter per server lets each keep the best era its own server
    # supports. `mode="legacy"` pins the handshake era; `mode="auto"` (the
    # default) negotiates the newest the server understands.
    legacy = Client(legacy_target, mode="legacy")
    modern = Client(modern_target, mode="auto")
    async with (
        MCPAdapter(legacy) as legacy_adapter,
        MCPAdapter(modern) as modern_adapter,
    ):
        return await legacy_adapter.list_tools() + await modern_adapter.list_tools()


# :snippet-end:


# :remove-start:
import asyncio
import warnings

from fastmcp import FastMCP
from fastmcp.utilities.tests import run_server_in_process
from langchain_core._api import LangChainBetaWarning

warnings.filterwarnings("ignore", category=LangChainBetaWarning)


def _weather_server() -> FastMCP:
    mcp: FastMCP = FastMCP("weather")

    @mcp.tool
    def get_forecast(city: str) -> str:
        """Report the forecast for a city."""
        return f"{city}: 18C and clear."

    return mcp


def _calculator_server() -> FastMCP:
    mcp: FastMCP = FastMCP("calculator")

    @mcp.tool
    def add(a: float, b: float) -> float:
        """Add two numbers."""
        return a + b

    return mcp


def _run_weather_http(host: str, port: int) -> None:
    _weather_server().run(
        transport="http", host=host, port=port, show_banner=False, log_level="warning"
    )


async def _run() -> None:
    with run_server_in_process(_run_weather_http) as url:
        tools = await load_tools(f"{url}/mcp")
        assert [t.name for t in tools] == ["get_forecast"]

    tools = await load_across_eras(_weather_server(), _calculator_server())
    assert sorted(t.name for t in tools) == ["add", "get_forecast"]
    print("✓ mcp-connections validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
