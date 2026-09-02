# :snippet-start: mcp-tool-errors-py
from langchain.mcp import MCPAdapter


async def divide_by_zero(server):
    async with MCPAdapter(server) as adapter:
        [divide] = await adapter.list_tools()

    # A server error (isError=True) reaches the model as a failed ToolMessage,
    # so the agent can read the server's own message and retry. Transport
    # failures still raise, because a model cannot act on those.
    return await divide.ainvoke(
        {"name": "divide", "args": {"a": 10, "b": 0}, "id": "1", "type": "tool_call"}
    )


# :snippet-end:


# :snippet-start: mcp-tool-metadata-py
from langchain.tools import BaseTool


def is_destructive(tool: BaseTool) -> bool:
    """Read the MCP destructive hint off the adapter's tool metadata.

    Every MCP tool the adapter produces carries provenance under an `mcp`
    namespace: annotations and `_meta` under `metadata["mcp"]["tool"]`, and the
    serving server's identity under `metadata["mcp"]["server"]`.
    """
    annotations = (
        (tool.metadata or {}).get("mcp", {}).get("tool", {}).get("annotations", {})
    )
    return annotations.get("destructive_hint", False)


# :snippet-end:


# :remove-start:
import asyncio
import warnings

from fastmcp import FastMCP
from langchain_core._api import LangChainBetaWarning

warnings.filterwarnings("ignore", category=LangChainBetaWarning)


def calculator_server() -> FastMCP:
    mcp: FastMCP = FastMCP("calculator")

    @mcp.tool
    def divide(a: float, b: float) -> float:
        """Divide a by b."""
        if b == 0:
            msg = "Cannot divide by zero."
            raise ValueError(msg)
        return a / b

    return mcp


async def _run() -> None:
    message = await divide_by_zero(calculator_server())
    assert message.status == "error"
    assert "zero" in message.text.lower()

    async with MCPAdapter(calculator_server()) as adapter:
        [divide] = await adapter.list_tools()
    assert divide.metadata["mcp"]["server"]["name"] == "calculator"
    assert is_destructive(divide) is False
    print("✓ mcp-tool-results validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
