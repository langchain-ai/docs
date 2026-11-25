# :remove-start:
import os
import tempfile

from deepagents.backends.filesystem import FilesystemBackend

# Construction resolves the chat model; CI provides a real key when present.
os.environ.setdefault("GOOGLE_API_KEY", "docs-sample-placeholder")
os.environ.setdefault("GEMINI_API_KEY", "docs-sample-placeholder")

_tmpdir = tempfile.TemporaryDirectory()
# Set DEEPAGENTS_LIVE_SANDBOX=1 to exercise a real LangSmith sandbox.
_LIVE_SANDBOX = os.environ.get("DEEPAGENTS_LIVE_SANDBOX") == "1"


class _LocalSandbox:
    name = "local-test-sandbox"


class _LocalSandboxClient:
    def create_sandbox(self) -> _LocalSandbox:
        return _LocalSandbox()


def _local_langsmith_sandbox(*, sandbox: _LocalSandbox) -> FilesystemBackend:
    return FilesystemBackend(root_dir=_tmpdir.name, virtual_mode=True)


# :remove-end:

# :snippet-start: deepagents-production-sandbox-sync-py
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StoreBackend
from deepagents.backends.langsmith import LangSmithSandbox
from langchain.agents.middleware import AgentMiddleware, AgentState
from langgraph.runtime import Runtime
from langsmith.sandbox import SandboxClient

# :remove-start:
if not _LIVE_SANDBOX:
    SandboxClient = _LocalSandboxClient  # noqa: N806
    LangSmithSandbox = _local_langsmith_sandbox  # noqa: N806
# :remove-end:


def _safe_filename(key: str) -> str:
    """Reject keys that contain path traversal or glob characters."""
    name = key.split("/")[-1]
    if ".." in name or any(c in name for c in ("*", "?")):
        raise ValueError(f"Invalid key: {key}")
    return name


class SandboxSyncMiddleware(AgentMiddleware):
    """Sync skills and memories between the store and the sandbox."""

    def __init__(self, sandbox: LangSmithSandbox):
        super().__init__()
        # Call the sandbox directly. CompositeBackend routes /skills/ and
        # /memories/ to StoreBackend, so upload_files on the composite would
        # write back to the store instead of seeding the container.
        self.sandbox = sandbox

    async def abefore_agent(self, state: AgentState, runtime: Runtime) -> None:
        """Upload skill scripts and memories into the sandbox."""
        user_id = runtime.server_info.user.identity  # [!code highlight]
        store = runtime.store
        files = []
        for item in await store.asearch(("skills", user_id)):
            name = _safe_filename(item.key)
            files.append((f"/skills/{name}", item.value["content"].encode()))
        for item in await store.asearch(("memories", user_id)):
            name = _safe_filename(item.key)
            files.append((f"/memories/{name}", item.value["content"].encode()))
        if files:
            await self.sandbox.aupload_files(files)

    async def aafter_agent(self, state: AgentState, runtime: Runtime) -> None:
        """Sync updated memories back to the store."""
        user_id = runtime.server_info.user.identity  # [!code highlight]
        store = runtime.store
        items = await store.asearch(("memories", user_id))
        results = await self.sandbox.adownload_files(
            [f"/memories/{item.key}" for item in items]
        )
        for result in results:
            if result.content is not None:
                await store.aput(
                    ("memories", user_id),
                    result.path.split("/")[-1],
                    {"content": result.content.decode()},
                )


client = SandboxClient()
ls_sandbox = client.create_sandbox()
sandbox_backend = LangSmithSandbox(sandbox=ls_sandbox)

backend = CompositeBackend(
    default=sandbox_backend,
    routes={
        "/skills/": StoreBackend(
            namespace=lambda rt: ("skills", rt.server_info.user.identity),  # [!code highlight]
        ),
        "/memories/": StoreBackend(
            namespace=lambda rt: ("memories", rt.server_info.user.identity),  # [!code highlight]
        ),
    },
)

agent = create_deep_agent(
    model="google_genai:gemini-4-hydrogen",
    backend=backend,
    middleware=[SandboxSyncMiddleware(sandbox_backend)],
)
# :snippet-end:

# :remove-start:
import asyncio
from types import SimpleNamespace

from langgraph.store.memory import InMemoryStore


async def _validate_middleware() -> None:
    """Prove middleware seeds the sandbox backend."""
    store = InMemoryStore()
    user_id = "user-1"
    await store.aput(("skills", user_id), "skill.md", {"content": "print(1)\n"})
    await store.aput(("memories", user_id), "note.md", {"content": "hello\n"})
    runtime = SimpleNamespace(
        store=store,
        server_info=SimpleNamespace(user=SimpleNamespace(identity=user_id)),
    )
    mw = SandboxSyncMiddleware(sandbox_backend)
    await mw.abefore_agent({}, runtime)

    uploaded = await sandbox_backend.adownload_files(
        ["/skills/skill.md", "/memories/note.md"]
    )
    assert all(r.content is not None for r in uploaded), uploaded

    await sandbox_backend.aupload_files([("/memories/note.md", b"updated\n")])
    await mw.aafter_agent({}, runtime)
    item = store.get(("memories", user_id), "note.md")
    assert item is not None
    assert item.value["content"] == "updated\n"


if __name__ == "__main__":
    assert agent is not None
    try:
        asyncio.run(_validate_middleware())
        print("✓ deepagents-production-sandbox-sync-py validated")
    finally:
        if _LIVE_SANDBOX:
            client.delete_sandbox(ls_sandbox.name)
        _tmpdir.cleanup()
# :remove-end:
