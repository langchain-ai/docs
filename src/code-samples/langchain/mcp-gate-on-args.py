# :snippet-start: mcp-gate-on-args-py
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.agents.middleware.human_in_the_loop import InterruptOnConfig
from langchain.mcp import MCPAdapter
from langchain.tools.tool_node import ToolCallRequest
from langgraph.checkpoint.memory import InMemorySaver


def _under_etc(request: ToolCallRequest) -> bool:
    # `when` receives the pending tool call, so the gate can read its arguments.
    return request.tool_call["args"].get("path", "").startswith("/etc")


async def gate_on_arguments(server):
    async with MCPAdapter(server) as adapter:
        tools = await adapter.list_tools()

        # Pause `delete_file` only when it targets a protected path; other
        # calls to the same tool run untouched.
        interrupt_on: dict[str, bool | InterruptOnConfig] = {
            "delete_file": InterruptOnConfig(
                allowed_decisions=["approve", "reject"], when=_under_etc
            )
        }
        return create_agent(
            "claude-sonnet-4-6",
            tools,
            middleware=[HumanInTheLoopMiddleware(interrupt_on=interrupt_on)],
            checkpointer=InMemorySaver(),
            system_prompt="Call delete_file with the exact path the user names.",
        )


# :snippet-end:


# :remove-start:
import asyncio
import warnings
from typing import Any

from fastmcp import FastMCP
from langchain_core._api import LangChainBetaWarning
from langgraph.types import Command

warnings.filterwarnings("ignore", category=LangChainBetaWarning)


def files_server() -> FastMCP:
    mcp: FastMCP = FastMCP("files")

    @mcp.tool
    def delete_file(path: str) -> str:
        """Delete a file from the workspace."""
        return f"Deleted {path}."

    return mcp


async def _run() -> None:
    agent = await gate_on_arguments(files_server())

    # A protected path pauses for approval.
    protected: Any = {"configurable": {"thread_id": "a"}}
    etc = {"messages": [{"role": "user", "content": "Delete /etc/hosts."}]}
    paused = await agent.ainvoke(etc, protected)
    assert "__interrupt__" in paused
    resumed = await agent.ainvoke(
        Command(resume={"decisions": [{"type": "approve"}]}), protected
    )
    assert resumed["messages"][-1].text

    # An ordinary path runs without pausing.
    ordinary: Any = {"configurable": {"thread_id": "b"}}
    done = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Delete report.md."}]}, ordinary
    )
    assert "__interrupt__" not in done
    print("✓ mcp-gate-on-args validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
