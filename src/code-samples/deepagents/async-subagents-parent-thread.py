"""Async subagents: find a supervisor's subagent threads."""

# :snippet-start: async-subagents-parent-thread-py
from langchain_core.runnables import RunnableConfig
from langgraph_sdk import get_client

from deepagents import create_deep_agent


async def find_subagent_threads(parent_thread_id: str) -> list[dict]:
    client = get_client()
    return await client.threads.search(metadata={"parent_thread_id": parent_thread_id})


def researcher(config: RunnableConfig):
    # Set when a supervisor launched this run with `start_async_task`
    parent_thread_id = (config.get("metadata") or {}).get("parent_thread_id")
    # :remove-start:
    assert parent_thread_id == "thread-supervisor"
    # :remove-end:
    return create_deep_agent(
        # KEEP MODEL
        model="google_genai:gemini-3.8-flash",
        system_prompt="You research topics thoroughly.",
    )
# :snippet-end:

# :remove-start:
assert researcher({"metadata": {"parent_thread_id": "thread-supervisor"}}) is not None
print("✓ async-subagents-parent-thread sample validated")
# :remove-end:
