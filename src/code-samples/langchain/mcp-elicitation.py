# :snippet-start: mcp-elicitation-py
from typing import Any

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command


async def book_with_elicitation(server) -> dict:
    # Elicitation is handled automatically: when a server needs input mid-call,
    # the adapter surfaces the question as a LangGraph `interrupt()`, so the
    # person already reviewing the agent's work answers it and the run resumes.
    async with MCPAdapter(server) as adapter:
        tools = await adapter.list_tools()

        # Resuming a paused run needs persistence, so the interrupted run has
        # somewhere to wait.
        agent = create_agent("claude-sonnet-4-6", tools, checkpointer=InMemorySaver())
        config: Any = {"configurable": {"thread_id": "booking-1"}}

        paused = await agent.ainvoke(
            {"messages": [{"role": "user", "content": "Book a table for 4."}]}, config
        )
        [interrupt] = paused["__interrupt__"]
        [question] = interrupt.value["requests"]

        # Answers are keyed by the server's own request key, so nothing has to
        # be tracked across the pause. `decline` or `cancel` would refuse.
        answer = {"action": "accept", "content": {"date": "2026-09-14"}}
        return await agent.ainvoke(
            Command(resume={"responses": {question["key"]: answer}}), config
        )


# :snippet-end:


# :snippet-start: mcp-destructive-gate-py
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.agents.middleware.human_in_the_loop import InterruptOnConfig
from langchain_core.tools import BaseTool


def is_destructive(tool: BaseTool) -> bool:
    """Read the MCP destructive hint off the adapter's tool metadata."""
    annotations = (
        (tool.metadata or {}).get("mcp", {}).get("tool", {}).get("annotations", {})
    )
    return annotations.get("destructive_hint", False)


async def gate_destructive_tools(server) -> tuple:
    async with MCPAdapter(server) as adapter:
        tools = await adapter.list_tools()

        # Build the interrupt map from metadata, not hardcoded tool names, so it
        # covers whatever destructive tools a server happens to expose.
        interrupt_on: dict[str, bool | InterruptOnConfig] = {
            tool.name: InterruptOnConfig(allowed_decisions=["approve", "reject"])
            for tool in tools
            if is_destructive(tool)
        }
        agent = create_agent(
            "claude-sonnet-4-6",
            tools,
            middleware=[HumanInTheLoopMiddleware(interrupt_on=interrupt_on)],
            checkpointer=InMemorySaver(),
        )
        return agent, interrupt_on


# :snippet-end:


# :remove-start:
import asyncio
import warnings

from fastmcp import Context, FastMCP
from langchain_core._api import LangChainBetaWarning
from mcp.types import (
    ElicitRequest,
    ElicitRequestFormParams,
    ElicitResult,
    InputRequiredResult,
    TextContent,
    ToolAnnotations,
)

warnings.filterwarnings("ignore", category=LangChainBetaWarning)


def booking_server() -> FastMCP:
    mcp: FastMCP = FastMCP("booking")

    @mcp.tool
    async def book_table(
        party_size: int, ctx: Context
    ) -> list[TextContent] | InputRequiredResult:
        """Book a restaurant table. Asks the user which date to book."""
        answers = ctx.input_responses
        if not answers or "date" not in answers:
            return InputRequiredResult(
                input_requests={
                    "date": ElicitRequest(
                        method="elicitation/create",
                        params=ElicitRequestFormParams(
                            mode="form",
                            message="What date would you like to book?",
                            requested_schema={
                                "type": "object",
                                "properties": {
                                    "date": {"type": "string", "format": "date"}
                                },
                                "required": ["date"],
                            },
                        ),
                    )
                },
                request_state="awaiting-date",
            )
        answer = answers["date"]
        if (
            not isinstance(answer, ElicitResult)
            or answer.action != "accept"
            or not answer.content
        ):
            return [
                TextContent(type="text", text="No date given, so nothing was booked.")
            ]
        booked = f"Booked a table for {party_size} on {answer.content['date']}."
        return [TextContent(type="text", text=booked)]

    return mcp


def files_server() -> FastMCP:
    mcp: FastMCP = FastMCP("files")

    @mcp.tool
    def list_files() -> list[str]:
        """List the files in the workspace."""
        return ["report.md", "notes.txt"]

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
    def delete_file(path: str) -> str:
        """Delete a file from the workspace."""
        return f"Deleted {path}."

    return mcp


async def _run() -> None:
    resumed = await book_with_elicitation(booking_server())
    assert resumed["messages"][-1].text

    agent, interrupt_on = await gate_destructive_tools(files_server())
    assert sorted(interrupt_on) == ["delete_file"]
    config: Any = {"configurable": {"thread_id": "files-1"}}
    paused = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Delete report.md."}]}, config
    )
    assert "__interrupt__" in paused
    resumed = await agent.ainvoke(
        Command(resume={"decisions": [{"type": "approve"}]}), config
    )
    assert resumed["messages"][-1].text
    print("✓ mcp-elicitation validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
