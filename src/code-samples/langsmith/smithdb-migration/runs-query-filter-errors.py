
# :snippet-start: runs-query-filter-errors-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
runs = client.list_runs(project_name="default", error=True)
# :snippet-end:

# :snippet-start: runs-query-filter-errors-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    project = await client.aread_project(project_name="default")
    runs = client.runs.query(project_ids=[str(project.id)], has_error=True)


asyncio.run(main())
# :snippet-end:
