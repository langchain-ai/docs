
# :snippet-start: runs-query-selecting-fields-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
# returns a default set of fields; no explicit selection needed
runs = client.list_runs(project_name="default")
for run in runs:
    print(run.id, run.name, run.run_type, run.status, run.start_time, run.inputs, run.error)
    # :remove-start:
    break
    # :remove-end:
# :snippet-end:

# :snippet-start: runs-query-selecting-fields-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    async for project in client.projects.list(name="default", limit=1):
        break
    # must explicitly list every field needed; default returns only id
    async for run in client.runs.query(
        project_ids=[str(project.id)],
        selects=["ID", "NAME", "RUN_TYPE", "STATUS", "START_TIME", "INPUTS", "ERROR"],
    ):
        print(run.id, run.name, run.run_type, run.status, run.start_time, run.inputs, run.error)
        # :remove-start:
        break
        # :remove-end:


asyncio.run(main())
# :snippet-end:
