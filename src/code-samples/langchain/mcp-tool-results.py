# :snippet-start: mcp-tool-errors-py
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain.messages import ToolMessage


async def divide_by_zero(server) -> dict:
    async with MCPAdapter(server) as adapter:
        tools = await adapter.list_tools()
        agent = create_agent("claude-sonnet-5", tools)
        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Use the divide tool to calculate 10 divided by 0.",
                    }
                ]
            }
        )

    # A server error (isError=True) reaches the model as a failed ToolMessage,
    # so the agent can read the server's own message and recover. Transport
    # failures still raise, because a model cannot act on those.
    for message in result["messages"]:
        if isinstance(message, ToolMessage) and message.status == "error":
            print(f"Tool reported: {message.text}")  # [!code highlight]

    return result


# :snippet-end:


# :snippet-start: mcp-tool-metadata-py
from langchain.tools import BaseTool


def is_destructive(tool: BaseTool) -> bool:
    """Read the MCP destructive hint off the adapter's tool metadata."""
    # Chain `.get` with defaults so a tool missing any nested field returns
    # False rather than raising.
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
    result = await divide_by_zero(calculator_server())
    failures = [
        message
        for message in result["messages"]
        if isinstance(message, ToolMessage) and message.status == "error"
    ]
    if failures:
        assert "zero" in failures[0].text.lower()
    else:
        assistant_text = "\n".join(
            getattr(message, "text", "")
            for message in result["messages"]
            if getattr(message, "type", None) == "ai"
        )
        assert "zero" in assistant_text.lower(), (
            "expected either a failed ToolMessage or an assistant response that mentions zero"
        )

    async with MCPAdapter(calculator_server()) as adapter:
        [divide] = await adapter.list_tools()
    assert divide.metadata["mcp"]["server"]["name"] == "calculator"
    assert is_destructive(divide) is False
    print("✓ mcp-tool-results validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
