
# :snippet-start: runs-query-boolean-filters-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
filter_str = (
    'and(gt(start_time, "2023-07-15T12:34:56Z"),'
    ' or(neq(status, "error"),'
    '    and(eq(feedback_key, "Correctness"), eq(feedback_score, 0.0))))'
)
runs = client.list_runs(project_name="default", filter=filter_str)
# :snippet-end:

# :snippet-start: runs-query-boolean-filters-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    filter_str = (
        'and(gt(start_time, "2023-07-15T12:34:56Z"),'
        ' or(neq(status, "error"),'
        '    and(eq(feedback_key, "Correctness"), eq(feedback_score, 0.0))))'
    )
    project = await client.aread_project(project_name="default")
    runs = client.runs.query(project_ids=[str(project.id)], filter=filter_str)


asyncio.run(main())
# :snippet-end:
