# :snippet-start: skills-sandbox-py
import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from daytona import Daytona
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StoreBackend
from deepagents.backends.protocol import SandboxBackendProtocol
from deepagents.backends.utils import create_file_data
from langchain.agents.middleware import AgentMiddleware, AgentState

# :remove-start:
from langchain.messages import HumanMessage

# :remove-end:
from langchain_daytona import DaytonaSandbox
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore

SKILLS_ROOT = "/tmp/skills"


def _sandbox_path_for_store_key(key: str) -> str:
    """Map a store object key to an absolute sandbox path under a writable skills root."""
    if ".." in key or any(c in key for c in ("*", "?")):
        msg = f"Invalid key: {key}"
        raise ValueError(msg)
    normalized = key if key.startswith("/") else f"/{key}"
    return f"{SKILLS_ROOT}{normalized}"


def _store_value_to_bytes(value: dict[str, Any]) -> bytes:
    raw = value["content"]
    if isinstance(raw, list):
        return ("\n".join(raw)).encode("utf-8")
    if isinstance(raw, str):
        return raw.encode("utf-8")
    return bytes(raw)


@dataclass
class AppContext:
    """Per-invocation context; use the same ``user_id`` you seed into the store."""

    user_id: str


class SkillSandboxSyncMiddleware(AgentMiddleware[AgentState, AppContext, Any]):
    """Upload skill files from the store into the sandbox before each agent run."""

    def __init__(self, sandbox_backend: SandboxBackendProtocol) -> None:
        super().__init__()
        self.sandbox_backend = sandbox_backend

    async def abefore_agent(
        self, state: AgentState, runtime: Runtime[AppContext]
    ) -> None:
        # In local/SDK runs, `server_info` may be unset; use the invocation context.
        if runtime.server_info is not None:
            user_id = runtime.server_info.user.identity
        else:
            user_id = runtime.context.user_id
        store = runtime.store

        files: list[tuple[str, bytes]] = []
        for item in await store.asearch(("skills", user_id)):
            dest = _sandbox_path_for_store_key(str(item.key))
            files.append((dest, _store_value_to_bytes(item.value)))

        if files:
            await self.sandbox_backend.aupload_files(files)


async def seed_skill_store(store: InMemoryStore, user_id: str) -> None:
    namespace = ("skills", user_id)
    skills_dir = Path(__file__).resolve().parent / "skills"
    for file_path in sorted(p for p in skills_dir.rglob("*") if p.is_file()):
        rel = file_path.relative_to(skills_dir).as_posix()
        key = f"/{rel}"
        await store.aput(
            namespace,
            key,
            create_file_data(file_path.read_text(encoding="utf-8")),
        )


async def main() -> None:
    store = InMemoryStore()
    await seed_skill_store(store, "demo-user")

    daytona = Daytona()
    sandbox = daytona.create()
    sandbox_backend = DaytonaSandbox(sandbox=sandbox)

    backend = CompositeBackend(
        default=sandbox_backend,
        routes={
            f"{SKILLS_ROOT}/": StoreBackend(
                store=store,
                namespace=lambda rt: (
                    "skills",
                    rt.server_info.user.identity
                    if rt.server_info
                    else rt.context.user_id,
                ),
            ),
        },
    )

    try:
        agent = create_deep_agent(
            model="anthropic:claude-sonnet-4-6",
            backend=backend,
            skills=[f"{SKILLS_ROOT}/"],
            store=store,
            context_schema=AppContext,
            middleware=[SkillSandboxSyncMiddleware(sandbox_backend)],
        )

        # :remove-start:
        result = await agent.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            "Use the write-timestamp skill to write the current date and time "
                            "to a file, then tell me what you wrote."
                        ),
                    ),
                ],
            },
            context=AppContext(user_id="demo-user"),
            config={"configurable": {"thread_id": "skills-sandbox-demo"}},
        )

        messages = result.get("messages", [])
        if messages:
            print(getattr(messages[-1], "content", ""))
        # :remove-end:
    finally:
        sandbox.stop()


if __name__ == "__main__":
    asyncio.run(main())
# :snippet-end:
