
# :snippet-start: runs-query-fetch-by-id-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
runs = client.list_runs(id=["<run-id-1>", "<run-id-2>"])
# :snippet-end:

# :snippet-start: runs-query-fetch-by-id-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    project = await client.aread_project(project_name="default")
    runs = client.runs.query(
        project_ids=[str(project.id)],
        ids=["<run-id-1>", "<run-id-2>"],
    )


asyncio.run(main())
# :snippet-end:
