# :snippet-start: mcp-structured-content-py
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain.messages import ToolMessage


async def run_agent_structured(server) -> dict:
    async with MCPAdapter(server) as adapter:
        tools = await adapter.list_tools()
        agent = create_agent("claude-sonnet-5", tools)
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": "Look up user 42."}]}
        )

    # The adapter sets `artifact` only when the tool returned structured
    # content, so a non-None artifact always carries `structured_content`.
    for message in result["messages"]:
        if isinstance(message, ToolMessage) and message.artifact is not None:
            structured = message.artifact["structured_content"]  # [!code highlight]
            print(f"Structured content: {structured}")  # [!code highlight]

    return result


# :snippet-end:


# :remove-start:
import asyncio
import warnings

from fastmcp import FastMCP
from langchain_core._api import LangChainBetaWarning

warnings.filterwarnings("ignore", category=LangChainBetaWarning)


def user_server() -> FastMCP:
    mcp: FastMCP = FastMCP("users")

    @mcp.tool
    def get_user(user_id: int) -> dict:
        """Return a user record by ID."""
        return {"id": user_id, "name": "Alice", "plan": "pro"}

    return mcp


async def _run() -> None:
    result = await run_agent_structured(user_server())
    assert result["messages"][-1].text
    artifacts = [
        message.artifact
        for message in result["messages"]
        if isinstance(message, ToolMessage) and message.artifact is not None
    ]
    assert artifacts, "expected get_user to return structured content"
    assert artifacts[0]["structured_content"]["name"] == "Alice"
    print("✓ mcp-structured-content validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
