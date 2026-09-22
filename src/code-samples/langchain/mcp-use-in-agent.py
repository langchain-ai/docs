# :snippet-start: mcp-use-in-agent-py
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter


async def run_agent(server) -> dict:
    # Discover the server's tools, then hand them to the agent like any other
    # LangChain tools. The tools hold the client, so the agent stays usable
    # for the life of the adapter context.
    async with MCPAdapter(server) as adapter:
        tools = await adapter.list_tools()
        agent = create_agent("claude-sonnet-5", tools)
        return await agent.ainvoke(
            {
                "messages": [
                    {"role": "user", "content": "What is the forecast for Oslo?"}
                ]
            }
        )


# :snippet-end:


# :remove-start:
import asyncio
import warnings

from fastmcp import FastMCP
from langchain_core._api import LangChainBetaWarning

warnings.filterwarnings("ignore", category=LangChainBetaWarning)


def weather_server() -> FastMCP:
    mcp: FastMCP = FastMCP("weather")

    @mcp.tool
    def get_forecast(city: str) -> str:
        """Report the forecast for a city."""
        return f"{city}: 18C and clear."

    return mcp


async def _run() -> None:
    result = await run_agent(weather_server())
    assert result["messages"][-1].text
    print("✓ mcp-use-in-agent validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
