# :snippet-start: mcp-shared-pool-py
import httpx2
from fastmcp.client import Client
from fastmcp.client.group import ClientGroup
from fastmcp.client.transports import StreamableHttpTransport
from langchain.mcp import MCPAdapter

# One connection pool, shared by every server the deployment talks to.
_POOL = httpx2.AsyncHTTPTransport()


class _SharedPool(httpx2.AsyncBaseTransport):
    """Lend `_POOL` to each client without letting any client close it."""

    handle_async_request = _POOL.handle_async_request

    async def aclose(self) -> None: ...


def _client_factory(**kwargs: object) -> httpx2.AsyncClient:
    return httpx2.AsyncClient(transport=_SharedPool(), **kwargs)


async def load_over_shared_pool(servers: dict[str, str]) -> list:
    # Every client draws HTTP connections from the same pool, so a fleet of
    # servers does not each open its own.
    group = ClientGroup(
        {
            name: Client(
                StreamableHttpTransport(url, httpx_client_factory=_client_factory)
            )
            for name, url in servers.items()
        }
    )
    async with MCPAdapter(group) as adapter:
        return await adapter.list_tools()


# :snippet-end:


# :remove-start:
import asyncio
import warnings

from fastmcp import FastMCP
from fastmcp.utilities.tests import run_server_in_process
from langchain_core._api import LangChainBetaWarning

warnings.filterwarnings("ignore", category=LangChainBetaWarning)


def _run_server(host: str, port: int) -> None:
    mcp: FastMCP = FastMCP("s")

    @mcp.tool
    def ping() -> str:
        """Health check."""
        return "pong"

    mcp.run(
        transport="http", host=host, port=port, show_banner=False, log_level="warning"
    )


async def _run() -> None:
    with run_server_in_process(_run_server) as url:
        tools = await load_over_shared_pool({"a": f"{url}/mcp", "b": f"{url}/mcp"})
    assert sorted(t.name for t in tools) == ["a_ping", "b_ping"]
    print("✓ mcp-shared-pool validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
