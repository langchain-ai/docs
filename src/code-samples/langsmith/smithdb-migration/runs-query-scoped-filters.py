
# :snippet-start: runs-query-scoped-filters-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
runs = client.list_runs(
    project_name="default",
    filter='eq(name, "RetrieveDocs")',
    trace_filter='and(eq(feedback_key, "user_score"), eq(feedback_score, 1))',
    tree_filter='eq(name, "ExpandQuery")',
)
# :snippet-end:

# :snippet-start: runs-query-scoped-filters-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    async for project in client.projects.list(name="default", limit=1):
        break
    runs = client.runs.query(
        project_ids=[str(project.id)],
        filter='eq(name, "RetrieveDocs")',
        trace_filter='and(eq(feedback_key, "user_score"), eq(feedback_score, 1))',
        tree_filter='eq(name, "ExpandQuery")',
    )


asyncio.run(main())
# :snippet-end:
