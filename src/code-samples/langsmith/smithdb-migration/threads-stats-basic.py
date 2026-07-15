
import asyncio


async def find_thread_id(project_id: str) -> str:
    from langsmith import Client

    client = Client()
    async for thread in client.threads.query(
        project_id=project_id,
        min_start_time="2026-07-01T00:00:00Z",
        max_start_time="2026-07-31T23:59:59Z",
        page_size=5,
    ):
        return thread.thread_id
    raise RuntimeError("no threads found")


# :snippet-start: threads-stats-basic-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
project = client.read_project(project_name="default")
thread_id = "<thread-id>"
# :remove-start:
thread_id = asyncio.run(find_thread_id(str(project.id)))
# :remove-end:
stats = client.get_run_stats(
    project_ids=[project.id],
    filter=f'eq(thread_id, "{thread_id}")',
    is_root=True,
)
print(stats["run_count"], stats["total_tokens"], stats["total_cost"])
# :snippet-end:

# :snippet-start: threads-stats-basic-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    project = await client.aread_project(project_name="default")
    thread_id = "<thread-id>"
    # :remove-start:
    thread_id = await find_thread_id(str(project.id))
    # :remove-end:
    stats = await client.threads.stats(
        thread_id,
        session_id=str(project.id),
        selects=["TURNS", "TOTAL_TOKENS", "TOTAL_COST"],
    )
    print(stats.turns, stats.total_tokens, stats.total_cost)


asyncio.run(main())
# :snippet-end:
