# :snippet-start: long-term-memory-write-tool-inmemory-py
from dataclasses import dataclass
from typing import Any, cast

from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.runnables import Runnable
from langgraph.store.memory import InMemoryStore
from typing_extensions import TypedDict

# InMemoryStore saves data to an in-memory dictionary. Use a DB-backed store in production.
store = InMemoryStore()


@dataclass
class Context:
    user_id: str


# TypedDict defines the structure of user information for the LLM
class UserInfo(TypedDict):
    name: str


# Tool that allows agent to update user information (useful for chat applications)
@tool
def save_user_info(user_info: UserInfo, runtime: ToolRuntime[Context]) -> str:
    """Save user info."""
    # Access the store - same as that provided to `create_agent`
    assert runtime.store is not None
    store = runtime.store
    user_id = runtime.context.user_id
    # Store data in the store (namespace, key, data)
    store.put(("users",), user_id, cast("dict[str, Any]", user_info))
    return "Successfully saved user info."


agent: Runnable = create_agent(
    model="claude-sonnet-4-6",
    tools=[save_user_info],
    store=store,
    context_schema=Context,
)

# Run the agent
agent.invoke(
    {"messages": [{"role": "user", "content": "My name is John Smith"}]},
    # user_id passed in context to identify whose information is being updated
    context=Context(user_id="user_123"),
)

# You can access the store directly to get the value
item = store.get(("users",), "user_123")
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    # Test by putting data directly into the store
    store.put(("users",), "user_123", {"name": "John Smith"})

    # Verify data was saved
    saved_data = store.get(("users",), "user_123")
    assert saved_data is not None
    assert saved_data.value["name"] == "John Smith"

    print("✓ Write tool with InMemoryStore works correctly")
# :remove-end:
