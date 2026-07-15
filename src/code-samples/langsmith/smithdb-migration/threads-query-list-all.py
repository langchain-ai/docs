
# :snippet-start: threads-query-list-all-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
threads = client.list_threads(project_name="default")
for thread in threads:
    print(thread["thread_id"], thread["count"])
    # :remove-start:
    break
    # :remove-end:
# :snippet-end:

# :snippet-start: threads-query-list-all-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    project = await client.aread_project(project_name="default")
    async for thread in client.threads.query(
        project_id=str(project.id),
        min_start_time="2026-07-01T00:00:00Z",
        max_start_time="2026-07-31T23:59:59Z",
    ):
        print(thread.thread_id, thread.count)
        # :remove-start:
        break
        # :remove-end:


asyncio.run(main())
# :snippet-end:
