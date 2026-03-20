# :snippet-start: long-term-memory-write-tool-postgres-py
from dataclasses import dataclass
from typing import Any, cast

from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.runnables import Runnable
from langgraph.store.postgres import PostgresStore  # type: ignore[import-not-found]
from typing_extensions import TypedDict


@dataclass
class Context:
    user_id: str


class UserInfo(TypedDict):
    name: str


@tool
def save_user_info(user_info: UserInfo, runtime: ToolRuntime[Context]) -> str:
    """Save user info."""
    assert runtime.store is not None
    runtime.store.put(
        ("users",), runtime.context.user_id, cast("dict[str, Any]", user_info)
    )
    return "Successfully saved user info."


DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
# :remove-start:
import os
import sys
from pathlib import Path

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-key")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from conftest import get_postgres_uri, prepare_postgres_store

DB_URI = get_postgres_uri()
prepare_postgres_store(DB_URI)
# :remove-end:

with PostgresStore.from_conn_string(DB_URI) as store:
    store.setup()
    agent: Runnable = create_agent(
        "claude-sonnet-4-6",
        tools=[save_user_info],
        store=store,
        context_schema=Context,
    )

    agent.invoke(
        {"messages": [{"role": "user", "content": "My name is John Smith"}]},
        context=Context(user_id="user_123"),
    )
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    with PostgresStore.from_conn_string(DB_URI) as store:
        store.setup()
        store.put(("users",), "user_123", {"name": "John Smith"})
        saved_data = store.get(("users",), "user_123")
        assert saved_data is not None
        assert saved_data.value["name"] == "John Smith"
    print("✓ Write tool with PostgresStore works correctly")
# :remove-end:
