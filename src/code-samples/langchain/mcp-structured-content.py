# :snippet-start: mcp-structured-content-py
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter


async def run_agent_structured(server) -> dict:
    # Run the agent; structured content from any tool call is attached to the
    # ToolMessage as an artifact rather than folded into the model-visible text.
    async with MCPAdapter(server) as adapter:
        tools = await adapter.list_tools()
        agent = create_agent("claude-sonnet-5", tools)
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": "Look up user 42."}]}
        )

    # Inspect ToolMessages in the result for structured_content artifacts.
    for message in result["messages"]:
        if hasattr(message, "artifact") and message.artifact is not None:
            structured = message.artifact.get("structured_content")  # [!code highlight]
            if structured is not None:
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
    print("✓ mcp-structured-content validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
