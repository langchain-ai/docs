
# :snippet-start: runs-query-filter-time-range-before-py
# :codegroup-tab: Before
from datetime import datetime, timedelta

from langsmith import Client

client = Client()
runs = client.list_runs(
    project_name="default",
    start_time=datetime.now() - timedelta(days=1),
    run_type="llm",
)
# :snippet-end:

# :snippet-start: runs-query-filter-time-range-after-py
# :codegroup-tab: After
import asyncio
from datetime import datetime, timedelta

from langsmith import Client


async def main():
    client = Client()
    async for project in client.projects.list(name="default", limit=1):
        break
    runs = client.runs.query(
        project_ids=[str(project.id)],
        min_start_time=datetime.now() - timedelta(days=1),
        run_type="LLM",
    )


asyncio.run(main())
# :snippet-end:
