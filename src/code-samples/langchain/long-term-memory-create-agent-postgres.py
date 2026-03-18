# :snippet-start: long-term-memory-create-agent-postgres-py
from langchain.agents import create_agent
from langchain_core.runnables import Runnable
from langgraph.store.postgres import PostgresStore  # type: ignore[import-not-found]

DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
# :remove-start:
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from conftest import get_postgres_uri, prepare_postgres_store

DB_URI = get_postgres_uri()
prepare_postgres_store(DB_URI)
# :remove-end:

with PostgresStore.from_conn_string(DB_URI) as store:
    store.setup()
    agent: Runnable = create_agent(
        "claude-sonnet-4-6",
        tools=[],
        store=store,
    )
# :snippet-end:

# :remove-start:
assert agent is not None
print("✓ Agent with PostgresStore created successfully")
# :remove-end:
