# :snippet-start: runs-geturl-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
runs = list(client.list_runs(project_name="default", limit=1))
# :remove-start:
assert len(runs) > 0, "expected at least one run in the 'default' project"
# :remove-end:
run = runs[0]
url = client.get_run_url(run=run)
print(url)
# :snippet-end:

# :remove-start:
print("✓ runs-get-url-before validated")
# :remove-end:


# :snippet-start: runs-geturl-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    runs = list(client.list_runs(project_name="default", limit=1))
    # :remove-start:
    assert len(runs) > 0, "expected at least one run in the 'default' project"
    # :remove-end:
    run = runs[0]
    response = await client.runs.get_url(
        run.id,
        project_id=str(run.session_id),
        trace_id=str(run.trace_id),
        start_time=run.start_time.isoformat(),
    )
    print(response.url)


asyncio.run(main())
# :snippet-end:

# :remove-start:
print("✓ runs-get-url-after validated")
# :remove-end:
