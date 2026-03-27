# :snippet-start: long-term-memory-read-tool-postgres-py
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.runnables import Runnable
from langgraph.store.postgres import PostgresStore  # type: ignore[import-not-found]


@dataclass
class Context:
    user_id: str


DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
# :remove-start:
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from conftest import get_postgres_uri, prepare_postgres_store

DB_URI = get_postgres_uri()
prepare_postgres_store(DB_URI)
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-key")
# :remove-end:

with PostgresStore.from_conn_string(DB_URI) as store:
    store.setup()
    store.put(("users",), "user_123", {"name": "John Smith", "language": "English"})

    @tool
    def get_user_info(runtime: ToolRuntime[Context]) -> str:
        """Look up user info."""
        assert runtime.store is not None
        user_info = runtime.store.get(("users",), runtime.context.user_id)
        return str(user_info.value) if user_info else "Unknown user"

    agent: Runnable = create_agent(
        "claude-sonnet-4-6",
        tools=[get_user_info],
        store=store,
        context_schema=Context,
    )

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "look up user information"}]},
        context=Context(user_id="user_123"),
    )
# :snippet-end:

# :remove-start:
assert result is not None
assert "messages" in result
print("✓ Read tool with PostgresStore works correctly")
# :remove-end:
