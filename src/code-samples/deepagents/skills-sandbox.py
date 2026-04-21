# :snippet-start: skills-sandbox-py
import asyncio

# :remove-start:
from dataclasses import dataclass

# :remove-end:
from pathlib import Path
from typing import Any

from daytona import Daytona
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StoreBackend
from deepagents.backends.utils import create_file_data
from langchain.agents.middleware import AgentMiddleware, AgentState

# :remove-start:
from langchain.messages import HumanMessage

# :remove-end:
from langchain_daytona import DaytonaSandbox
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore


def _store_value_to_bytes(value: dict[str, Any]) -> bytes:
    raw = value["content"]
    if isinstance(raw, list):
        return ("\n".join(raw)).encode("utf-8")
    if isinstance(raw, str):
        return raw.encode("utf-8")
    return bytes(raw)


# :remove-start:
@dataclass
class AppContext:
    """Per-invocation context; use the same ``user_id`` you seed into the store."""

    user_id: str


# :remove-end:
class SkillSandboxSyncMiddleware(AgentMiddleware[AgentState, AppContext, Any]):
    """Upload skill files from the store into the sandbox before each agent run."""

    def __init__(self, backend: CompositeBackend) -> None:
        super().__init__()
        self.backend = backend

    async def abefore_agent(
        self, state: AgentState, runtime: Runtime[AppContext]
    ) -> None:
        # In local/SDK runs, `server_info` may be unset; use the invocation context.
        if runtime.server_info is not None:
            user_id = runtime.server_info.user.identity
        # :remove-start:
        else:
            user_id = runtime.context.user_id
        # :remove-end:
        store = runtime.store

        files: list[tuple[str, bytes]] = []
        for item in await store.asearch(("skills", user_id)):
            key = str(item.key)
            if ".." in key or any(c in key for c in ("*", "?")):
                msg = f"Invalid key: {key}"
                raise ValueError(msg)
            normalized = key if key.startswith("/") else f"/{key}"
            # CompositeBackend routes paths and batches uploads to the right backend.
            files.append((f"/skills{normalized}", _store_value_to_bytes(item.value)))

        if files:
            await self.backend.aupload_files(files)


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
            "/skills/": StoreBackend(
                store=store,
                namespace=lambda rt: (
                    "skills",
                    rt.server_info.user.identity
                    if rt.server_info
                    # :remove-start:
                    else rt.context.user_id,
                    # :remove-end:
                ),
            ),
        },
    )

    try:
        agent = create_deep_agent(
            model="anthropic:claude-sonnet-4-6",
            backend=backend,
            skills=["/skills/"],
            store=store,
            context_schema=AppContext,
            middleware=[SkillSandboxSyncMiddleware(backend)],
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
            # :remove-start:
            context=AppContext(user_id="demo-user"),
            # :remove-end:
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
