# :remove-start:
import asyncio
import warnings
from pathlib import Path

from fastmcp import FastMCP
from langchain_core._api import LangChainBetaWarning

warnings.filterwarnings("ignore", category=LangChainBetaWarning)


def _weather_server() -> FastMCP:
    mcp: FastMCP = FastMCP("weather")

    @mcp.tool
    def get_forecast(city: str) -> str:
        """Report the forecast for a city."""
        return f"{city}: 18C and clear."

    return mcp


# Make the targets the snippet names real, so its constructors run: `server` is
# an in-process server, and `weather_server.py` is a script on disk.
server = _weather_server()
_SCRIPT = Path("weather_server.py")
_SCRIPT.write_text(
    "from fastmcp import FastMCP\n"
    "mcp = FastMCP('weather')\n"
    "if __name__ == '__main__':\n"
    "    mcp.run()\n"
)
# :remove-end:
# :snippet-start: mcp-transports-py
from pathlib import Path

from langchain.mcp import MCPAdapter

# An in-process FastMCP server: no subprocess, no socket. Ideal for tests.
in_memory = MCPAdapter(server)  # a FastMCP instance

# A script path is launched over stdio, one subprocess per adapter.
stdio = MCPAdapter(Path("weather_server.py"))

# A string must be an http(s) URL, reached over streamable HTTP.
http = MCPAdapter("https://example.com/mcp")
# :snippet-end:


# :remove-start:
async def _run() -> None:
    # The in-process adapter actually connects and lists tools.
    async with in_memory as adapter:
        assert [t.name for t in await adapter.list_tools()] == ["get_forecast"]
    # The stdio and http adapters constructed above (targets are valid).
    assert stdio is not None
    assert http is not None
    _SCRIPT.unlink(missing_ok=True)
    print("✓ mcp-transports validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
