# :snippet-start: mcp-transports-py
from langchain.mcp import MCPAdapter


async def in_memory(server) -> list:
    # An in-process FastMCP server: no subprocess, no socket. Ideal for tests.
    async with MCPAdapter(server) as adapter:
        return await adapter.list_tools()


async def stdio(script_path) -> list:
    # A script path is launched over stdio, one subprocess per adapter.
    async with MCPAdapter(script_path) as adapter:
        return await adapter.list_tools()


async def http(url: str) -> list:
    # A string must be an http(s) URL, reached over streamable HTTP.
    async with MCPAdapter(url) as adapter:
        return await adapter.list_tools()


# :snippet-end:


# :remove-start:
import asyncio
import tempfile
import textwrap
import warnings
from pathlib import Path

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


def _run_weather_http(host: str, port: int) -> None:
    _weather_server().run(
        transport="http", host=host, port=port, show_banner=False, log_level="warning"
    )


def _write_stdio_server() -> Path:
    path = Path(tempfile.mkstemp(suffix=".py", prefix="mcp-stdio-")[1])
    path.write_text(
        textwrap.dedent(
            """
            from fastmcp import FastMCP

            mcp = FastMCP("weather")

            @mcp.tool
            def get_forecast(city: str) -> str:
                "Report the forecast for a city."
                return f"{city}: 18C and clear."

            if __name__ == "__main__":
                mcp.run()
            """
        )
    )
    return path


async def _run() -> None:
    tools = await in_memory(_weather_server())
    assert [t.name for t in tools] == ["get_forecast"]

    stdio_server = _write_stdio_server()
    try:
        tools = await stdio(stdio_server)
        assert [t.name for t in tools] == ["get_forecast"]
    finally:
        stdio_server.unlink(missing_ok=True)

    with run_server_in_process(_run_weather_http) as url:
        tools = await http(f"{url}/mcp")
        assert [t.name for t in tools] == ["get_forecast"]

    print("✓ mcp-transports validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
