
# :snippet-start: runs-query-list-root-as-traces-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
project = client.read_project(project_name="default")

root_runs = list(client.list_runs(project_id=project.id, is_root=True, limit=5))
for root_run in root_runs:
    print(root_run.trace_id, root_run.name)
# :snippet-end:

# :snippet-start: runs-query-list-root-as-traces-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    project = await client.aread_project(project_name="default")
    count = 0
    async for trace in client.traces.query(
        project_id=str(project.id),
        min_start_time="2026-07-01T00:00:00Z",
        max_start_time="2026-07-31T23:59:59Z",
        selects=["NAME"],
    ):
        print(trace.root_run.trace_id, trace.root_run.name)
        count += 1
        if count >= 5:
            break


asyncio.run(main())
# :snippet-end:
