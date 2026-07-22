
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


# :snippet-start: threads-list-traces-basic-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
thread_id = "<thread-id>"
# :remove-start:
project = client.read_project(project_name="default")
thread_id = asyncio.run(find_thread_id(str(project.id)))
# :remove-end:
for run in client.read_thread(thread_id=thread_id, project_name="default"):
    print(run.id, run.start_time)
    # :remove-start:
    break
    # :remove-end:
# :snippet-end:

# :snippet-start: threads-list-traces-basic-after-py
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
    async for trace in client.threads.list_traces(
        thread_id, project_id=str(project.id), selects=["START_TIME"]
    ):
        print(trace.trace_id, trace.start_time)
        # :remove-start:
        break
        # :remove-end:


asyncio.run(main())
# :snippet-end:
