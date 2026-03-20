# :snippet-start: long-term-memory-storage-postgres-py
from collections.abc import Sequence

from langgraph.store.base import IndexConfig
from langgraph.store.postgres import PostgresStore  # type: ignore[import-not-found]


def embed(texts: Sequence[str]) -> list[list[float]]:
    # Replace with an actual embedding function or LangChain embeddings object
    return [[1.0, 2.0] for _ in texts]


DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
# :remove-start:
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from conftest import get_postgres_uri, prepare_postgres_store

DB_URI = get_postgres_uri()
prepare_postgres_store(DB_URI)
# :remove-end:

with PostgresStore.from_conn_string(
    DB_URI,
    index=IndexConfig(embed=embed, dims=2),  # type: ignore[arg-type]
) as store:
    store.setup()
    user_id = "my-user"
    application_context = "chitchat"
    namespace = (user_id, application_context)
    store.put(
        namespace,
        "a-memory",
        {
            "rules": [
                "User likes short, direct language",
                "User only speaks English & python",
            ],
            "my-key": "my-value",
        },
    )
    item = store.get(namespace, "a-memory")
    items = store.search(
        namespace, filter={"my-key": "my-value"}, query="language preferences"
    )
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert item is not None
    assert item.value["my-key"] == "my-value"
    assert "rules" in item.value
    assert len(item.value["rules"]) == 2
    assert len(items) > 0
    print("✓ PostgresStore operations work correctly")
# :remove-end:
