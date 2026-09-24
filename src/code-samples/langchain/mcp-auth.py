# :snippet-start: mcp-auth-bearer-py
from fastmcp.client import Client
from langchain.mcp import MCPAdapter


async def load_tools_with_bearer(url: str, token: str) -> list:
    # `auth` accepts a bearer-token string, the literal "oauth" (full OAuth 2.1
    # with dynamic client registration), or any `httpx.Auth`.
    async with MCPAdapter(Client(url, auth=token)) as adapter:
        return await adapter.list_tools()


# :snippet-end:


# :snippet-start: mcp-auth-oauth-py
async def load_tools_with_oauth(url: str) -> list:
    # "oauth" runs discovery, dynamic client registration, the browser redirect,
    # and the token exchange. Pass `OAuth(..., token_storage=...)` to persist
    # tokens across runs instead of repeating the browser step each time.
    async with MCPAdapter(Client(url, auth="oauth")) as adapter:
        return await adapter.list_tools()


# :snippet-end:


# :snippet-start: mcp-auth-per-server-py
from fastmcp.client.group import ClientGroup


async def load_with_per_server_auth(
    billing_url: str, docs_token: str, docs_url: str
) -> list:
    # Each server carries its own credential. A `ClientGroup` keeps one
    # connection per server, so each authenticates independently.
    group = ClientGroup(
        {
            "billing": Client(billing_url, auth="oauth"),
            "docs": Client(docs_url, auth=docs_token),
        }
    )
    async with MCPAdapter(group) as adapter:
        return await adapter.list_tools()


# :snippet-end:


# :remove-start:
import asyncio
import warnings

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier
from fastmcp.utilities.tests import run_server_in_process
from langchain_core._api import LangChainBetaWarning

warnings.filterwarnings("ignore", category=LangChainBetaWarning)

_TOKEN = "demo-weather-token"  # noqa: S105


def _run_guarded_server(host: str, port: int) -> None:
    mcp: FastMCP = FastMCP(
        "weather",
        auth=StaticTokenVerifier(
            tokens={_TOKEN: {"client_id": "demo", "scopes": ["read"]}}
        ),
    )

    @mcp.tool
    def get_forecast(city: str) -> str:
        """Report the forecast for a city."""
        return f"{city}: 18C and clear."

    mcp.run(
        transport="http", host=host, port=port, show_banner=False, log_level="warning"
    )


async def _run() -> None:
    with run_server_in_process(_run_guarded_server) as url:
        tools = await load_tools_with_bearer(f"{url}/mcp", _TOKEN)
        assert [t.name for t in tools] == ["get_forecast"]

        failed = False
        try:
            async with MCPAdapter(f"{url}/mcp") as adapter:
                await adapter.list_tools()
        except Exception:  # noqa: BLE001
            failed = True
        assert failed, "expected an unauthenticated call to fail"

        # Per-server auth: each client in a group carries its own credential.
        # Both point at the same guarded server here, each with the token.
        group = ClientGroup(
            {
                "billing": Client(f"{url}/mcp", auth=_TOKEN),
                "docs": Client(f"{url}/mcp", auth=_TOKEN),
            }
        )
        async with MCPAdapter(group) as adapter:
            tools = await adapter.list_tools()
        assert sorted(t.name for t in tools) == [
            "billing_get_forecast",
            "docs_get_forecast",
        ]
    print("✓ mcp-auth validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
