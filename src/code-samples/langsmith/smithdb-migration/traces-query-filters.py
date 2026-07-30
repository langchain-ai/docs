
# :snippet-start: traces-query-filters-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
project = client.read_project(project_name="default")

# v1 has no root-run-only filter concept — is_root plus a regular filter is
# the closest equivalent, still scanning every run to match.
error_traces = client.list_runs(
    project_id=project.id,
    is_root=True,
    filter='eq(status, "error")',
    limit=5,
)
for run in error_traces:
    print(run.trace_id)
# :snippet-end:

# :snippet-start: traces-query-filters-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    project = await client.aread_project(project_name="default")

    # trace_filter is implicitly root-run-only — no is_root needed.
    count = 0
    async for trace in client.traces.query(
        project_id=str(project.id),
        min_start_time="2026-07-01T00:00:00Z",
        max_start_time="2026-07-31T23:59:59Z",
        trace_filter='eq(status, "error")',
    ):
        print(trace.root_run.trace_id)
        count += 1
        if count >= 5:
            break

    # trace_ids is a fast-path when you already know which traces you want.
    trace_id = "<trace-id>"
    # :remove-start:
    async for t in client.traces.query(
        project_id=str(project.id),
        min_start_time="2026-07-01T00:00:00Z",
        max_start_time="2026-07-31T23:59:59Z",
        page_size=1,
    ):
        trace_id = t.root_run.trace_id
        break
    # :remove-end:
    async for trace in client.traces.query(
        project_id=str(project.id),
        min_start_time="2026-07-01T00:00:00Z",
        max_start_time="2026-07-31T23:59:59Z",
        trace_ids=[trace_id],
    ):
        print(trace.root_run.trace_id)


asyncio.run(main())
# :snippet-end:
