# :snippet-start: mcp-multi-server-py
from langchain.mcp import MCPAdapter

CONFIG = {
    "mcpServers": {
        "weather": {"command": "python", "args": ["/path/to/weather_server.py"]},
        "calc": {"command": "python", "args": ["/path/to/calc_server.py"]},
    }
}


async def load_fleet_tools(config: dict) -> list:
    async with MCPAdapter(config) as adapter:
        # Every tool is prefixed with its config key (`weather_...`, `calc_...`),
        # so two servers exposing the same tool name stay distinguishable.
        return await adapter.list_tools()


# :snippet-end:


# :remove-start:
import asyncio
import sys
import tempfile
import textwrap
import warnings
from pathlib import Path

from langchain_core._api import LangChainBetaWarning

warnings.filterwarnings("ignore", category=LangChainBetaWarning)


def _write_server(name: str, tool_name: str) -> Path:
    path = Path(tempfile.mkstemp(suffix=".py", prefix=f"mcp-{name}-")[1])
    path.write_text(
        textwrap.dedent(
            f"""
            from fastmcp import FastMCP

            mcp = FastMCP("{name}")

            @mcp.tool
            def {tool_name}(value: str) -> str:
                "A {name} tool."
                return "{name}: " + value

            if __name__ == "__main__":
                mcp.run()
            """
        )
    )
    return path


async def _run() -> None:
    weather = _write_server("weather", "forecast")
    calc = _write_server("calc", "forecast")
    try:
        config = {
            "mcpServers": {
                "weather": {"command": sys.executable, "args": [str(weather)]},
                "calc": {"command": sys.executable, "args": [str(calc)]},
            }
        }
        tools = await load_fleet_tools(config)
        assert sorted(t.name for t in tools) == ["calc_forecast", "weather_forecast"]
    finally:
        weather.unlink(missing_ok=True)
        calc.unlink(missing_ok=True)
    print("✓ mcp-multi-server validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
