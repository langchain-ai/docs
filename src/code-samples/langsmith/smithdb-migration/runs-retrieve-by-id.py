
import asyncio

async def find_run(project_id: str):
    client = Client()
    async for run in client.runs.query(project_ids=[project_id], selects=["ID", "START_TIME"]):
        return run
    return None

async def get_project_id():
    from langsmith import Client as AsyncClient
    client = AsyncClient()
    async for project in client.projects.list(name="default", limit=1):
        return project.id
    return None

# :snippet-start: runs-retrieve-by-id-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
run_id = "<run-id>"
# :remove-start:
project_id = asyncio.run(get_project_id())
run_id = asyncio.run(find_run(project_id)).id
# :remove-end:
run = client.read_run(run_id)
# :snippet-end:

# :snippet-start: runs-retrieve-by-id-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    async for project in client.projects.list(name="default", limit=1):
        break
    run_id = "<run-id>"
    start_time="2026-06-01T12:00:00Z"
    # :remove-start:
    run = await find_run(project.id)
    run_id = run.id
    start_time = run.start_time
    # :remove-end:
    run = await client.runs.retrieve(
        run_id=run_id,
        project_id=str(project.id),
        start_time=start_time,
    )


asyncio.run(main())
# :snippet-end:
