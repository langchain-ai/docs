# :snippet-start: long-term-memory-storage-inmemory-py
from collections.abc import Sequence

from langgraph.store.base import IndexConfig
from langgraph.store.memory import InMemoryStore


def embed(texts: Sequence[str]) -> list[list[float]]:
    # Replace with an actual embedding function or LangChain embeddings object
    return [[1.0, 2.0] for _ in texts]


# InMemoryStore saves data to an in-memory dictionary. Use a DB-backed store in production use.
store = InMemoryStore(index=IndexConfig(embed=embed, dims=2))
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
# get the "memory" by ID
item = store.get(namespace, "a-memory")
# search for "memories" within this namespace, filtering on content equivalence, sorted by vector similarity
items = store.search(
    namespace, filter={"my-key": "my-value"}, query="language preferences"
)
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    # Verify the operations work
    assert item is not None
    assert item.value["my-key"] == "my-value"
    assert "rules" in item.value
    assert len(item.value["rules"]) == 2

    # Verify search returns results
    assert len(items) > 0
    assert items[0].value["my-key"] == "my-value"

    print("✓ InMemoryStore operations work correctly")
# :remove-end:
