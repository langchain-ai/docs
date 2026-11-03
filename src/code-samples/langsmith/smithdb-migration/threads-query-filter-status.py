
# :snippet-start: threads-query-filter-status-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
threads = client.list_threads(project_name="default", filter='eq(status, "error")')
for thread in threads:
    print(thread["thread_id"])
    # :remove-start:
    break
    # :remove-end:
# :snippet-end:

# :snippet-start: threads-query-filter-status-after-py
# :codegroup-tab: After
import asyncio
from datetime import datetime, timedelta, timezone

from langsmith import Client


async def main():
    client = Client()
    project = await client.aread_project(project_name="default")
    async for thread in client.threads.query(
        project_id=str(project.id),
        min_start_time=datetime.now(timezone.utc) - timedelta(days=30),
        max_start_time=datetime.now(timezone.utc),
        filter='eq(status, "error")',
    ):
        print(thread.thread_id, thread.last_error)
        # :remove-start:
        break
        # :remove-end:


asyncio.run(main())
# :snippet-end:
