
# :snippet-start: runs-query-filter-metadata-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
filter_str = 'and(eq(metadata_key, "user_id"), eq(metadata_value, "u_123"))'
runs = client.list_runs(project_name="default", filter=filter_str)
# :snippet-end:

# :snippet-start: runs-query-filter-metadata-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    filter_str = 'and(eq(metadata_key, "user_id"), eq(metadata_value, "u_123"))'
    project = await client.aread_project(project_name="default")
    runs = client.runs.query(project_ids=[str(project.id)], filter=filter_str)


asyncio.run(main())
# :snippet-end:
