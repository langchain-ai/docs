# :remove-start:
from langsmith import uuid7
# :remove-end:


# :snippet-start: runs-add-to-queue-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
queue_id = "<queue-id>"
runs = list(client.list_runs(project_name="default", limit=5))
# :remove-start:
queue = client.create_annotation_queue(name=f"docs-smithdb-migration-{uuid7()}")
queue_id = str(queue.id)
assert len(runs) > 0, "expected at least one run in the 'default' project"
# :remove-end:
client.add_runs_to_annotation_queue(queue_id, run_ids=[run.id for run in runs])
# :snippet-end:

# :remove-start:
print("✓ runs-add-to-queue-before validated")
# :remove-end:


# :snippet-start: runs-add-to-queue-after-py
# :codegroup-tab: After
import asyncio
from datetime import datetime, timedelta, timezone

from langsmith import Client


async def main():
    client = Client()
    queue_id = "<queue-id>"
    project_id = "<project-id>"
    # :remove-start:
    project_id = str(client.read_project(project_name="default").id)
    queue = client.create_annotation_queue(name=f"docs-smithdb-migration-{uuid7()}")
    queue_id = str(queue.id)
    # :remove-end:
    page = await client.runs.query(
        project_ids=[project_id],
        min_start_time=datetime.now(timezone.utc) - timedelta(days=30),
        selects=["ID", "PROJECT_ID", "START_TIME"],
        page_size=5,
    )
    runs = page.items
    # :remove-start:
    assert len(runs) > 0, "expected at least one run in the 'default' project"
    # :remove-end:
    await client.annotation_queues.items.create(
        queue_id,
        items=[
            {
                "item_type": "RUN",
                "run_id": str(run.id),
                "project_id": str(run.project_id),
                "start_time": run.start_time.isoformat(),
            }
            for run in runs
        ],
    )


asyncio.run(main())
# :snippet-end:

# :remove-start:
print("✓ runs-add-to-queue-after validated")
# :remove-end:
