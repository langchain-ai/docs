
# :snippet-start: traces-list-runs-filter-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
project = client.read_project(project_name="default")
trace_id = "<trace-id>"
# :remove-start:
root_run = next(client.list_runs(project_id=project.id, is_root=True, limit=1))
trace_id = root_run.trace_id
# :remove-end:
llm_runs = list(
    client.list_runs(
        project_id=project.id,
        trace_id=trace_id,
        filter='eq(run_type, "llm")',
    )
)
# :snippet-end:

# :snippet-start: traces-list-runs-filter-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    project = await client.aread_project(project_name="default")
    trace_id = "<trace-id>"
    # :remove-start:
    async for t in client.traces.query(
        project_id=str(project.id),
        min_start_time="2026-07-01T00:00:00Z",
        max_start_time="2026-07-31T23:59:59Z",
    ):
        trace_id = t.root_run.trace_id
        break
    # :remove-end:
    response = await client.traces.list_runs(
        trace_id,
        project_id=str(project.id),
        filter='eq(run_type, "llm")',
        selects=["NAME", "STATUS"],
    )
    llm_runs = response.items


asyncio.run(main())
# :snippet-end:
