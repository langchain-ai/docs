# :snippet-start: mcp-quickstart-py
from langchain.mcp import MCPAdapter


async def load_tools(url: str) -> list:
    async with MCPAdapter(url) as adapter:
        # Tools hold the client, so they stay callable after the context exits.
        return await adapter.list_tools()


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
    async with MCPAdapter(weather_server()) as adapter:
        tools = await adapter.list_tools()
    assert [t.name for t in tools] == ["get_forecast"]
    [forecast] = tools
    blocks = await forecast.ainvoke({"city": "Oslo"})
    assert blocks[0]["text"] == "Oslo: 18C and clear."
    print("✓ mcp-quickstart validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
