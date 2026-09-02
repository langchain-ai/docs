# :snippet-start: deepagents-mcp-tools-py
import asyncio

from deepagents import create_deep_agent
from langchain.mcp import MCPAdapter


async def main():
    config = {"mcpServers": {"my_server": {"url": "http://localhost:8000/mcp"}}}
    async with MCPAdapter(config) as adapter:
        tools = await adapter.list_tools()

    agent = create_deep_agent(
        model="anthropic:claude-sonnet-4-6",
        tools=tools,
    )

    await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Use the MCP server to help me."}]},
        config={"configurable": {"thread_id": "1"}},
    )


# :snippet-end:


# :remove-start:
import warnings

from fastmcp import FastMCP
from fastmcp.utilities.tests import run_server_in_process
from langchain_core._api import LangChainBetaWarning

warnings.filterwarnings("ignore", category=LangChainBetaWarning)


def _run_server(host: str, port: int) -> None:
    mcp: FastMCP = FastMCP("my_server")

    @mcp.tool
    def ping() -> str:
        """Return a health check."""
        return "pong"

    mcp.run(
        transport="http", host=host, port=port, show_banner=False, log_level="warning"
    )


async def _run() -> None:
    # Validate the loading path against a real server without invoking a model.
    with run_server_in_process(_run_server) as url:
        adapter_config = {"mcpServers": {"my_server": {"url": f"{url}/mcp"}}}
        async with MCPAdapter(adapter_config) as adapter:
            tools = await adapter.list_tools()
        assert any(t.name.endswith("ping") for t in tools), [t.name for t in tools]
        agent = create_deep_agent(model="anthropic:claude-sonnet-4-6", tools=tools)
        assert agent is not None
    print("✓ deepagents-mcp-tools validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
