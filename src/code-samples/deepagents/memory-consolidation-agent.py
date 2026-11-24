"""Deep Agents memory: background consolidation agent."""

# :remove-start:
import os

# Construction resolves the chat model; CI provides a real key.
os.environ.setdefault("GOOGLE_API_KEY", "docs-sample-placeholder")
os.environ.setdefault("GEMINI_API_KEY", "docs-sample-placeholder")
# :remove-end:

# :snippet-start: memory-consolidation-agent-py
from datetime import datetime, timedelta, timezone

from deepagents import create_deep_agent
from langchain.tools import tool, ToolRuntime
from langgraph_sdk import get_client

sdk_client = get_client(url="<DEPLOYMENT_URL>")


@tool
async def search_recent_conversations(query: str, runtime: ToolRuntime) -> str:
    """Search this user's conversations updated in the last 6 hours."""
    user_id = runtime.server_info.user.identity  # [!code highlight]

    since = datetime.now(timezone.utc) - timedelta(hours=6)
    threads = await sdk_client.threads.search(
        metadata={"user_id": user_id},
        sort_by="updated_at",
        sort_order="desc",
        limit=20,
    )
    conversations = []
    for thread in threads:
        if datetime.fromisoformat(thread["updated_at"]) < since:
            break
        state = await sdk_client.threads.get_state(thread_id=thread["thread_id"])
        conversations.append(state["values"]["messages"])
    return str(conversations)


agent = create_deep_agent(
    model="google_genai:gemini-4-hydrogen",
    system_prompt="""Review recent conversations and update the user's memory file.
Merge new facts, remove outdated information, and keep it concise.""",
    tools=[search_recent_conversations],
)
# :snippet-end:

# :remove-start:
import asyncio
from types import SimpleNamespace


class _FakeThreads:
    def __init__(self, threads: list[dict]) -> None:
        self._threads = threads

    async def search(self, **kwargs: object) -> list[dict]:
        assert kwargs.get("sort_by") == "updated_at"
        assert kwargs.get("sort_order") == "desc"
        assert kwargs.get("limit") == 20
        assert kwargs.get("metadata") == {"user_id": "user-1"}
        return self._threads

    async def get_state(self, thread_id: str) -> dict:
        return {
            "values": {
                "messages": [{"role": "user", "content": f"msg-{thread_id}"}]
            }
        }


now = datetime.now(timezone.utc)
sdk_client.threads = _FakeThreads(
    [
        {
            "thread_id": "t-recent",
            "updated_at": (now - timedelta(hours=1)).isoformat(),
        },
        {
            "thread_id": "t-old",
            "updated_at": (now - timedelta(hours=10)).isoformat(),
        },
    ]
)

runtime = SimpleNamespace(
    server_info=SimpleNamespace(user=SimpleNamespace(identity="user-1"))
)


async def _main() -> None:
    assert search_recent_conversations.coroutine is not None
    out = await search_recent_conversations.coroutine("q", runtime)
    assert "msg-t-recent" in out
    assert "msg-t-old" not in out
    assert agent is not None
    print("✓ memory-consolidation-agent validated")


asyncio.run(_main())
# :remove-end:
