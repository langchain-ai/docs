
# :snippet-start: runs-query-pagination-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
runs = client.list_runs(project_name="default", limit=150)
# :snippet-end:

# :snippet-start: runs-query-pagination-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    async for project in client.projects.list(name="default", limit=1):
        break
    runs = []
    async for run in client.runs.query(
        project_ids=[str(project.id)],
    ):
        runs.append(run)
        if len(runs) >= 150:
            break


asyncio.run(main())
# :snippet-end:
