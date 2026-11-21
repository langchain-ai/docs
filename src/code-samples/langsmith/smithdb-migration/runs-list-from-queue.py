# :remove-start:
from langsmith import Client as _SetupClient
from langsmith import uuid7


def _seed_queue() -> str:
    """Create a queue holding one run from the 'default' project."""
    setup_client = _SetupClient()
    queue = setup_client.create_annotation_queue(
        name=f"docs-smithdb-migration-{uuid7()}"
    )
    runs = list(setup_client.list_runs(project_name="default", limit=1))
    assert len(runs) > 0, "expected at least one run in the 'default' project"
    setup_client.add_runs_to_annotation_queue(str(queue.id), run_ids=[runs[0].id])
    return str(queue.id)


# :remove-end:


# :snippet-start: runs-list-from-queue-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
queue_id = "<queue-id>"
# :remove-start:
queue_id = _seed_queue()
# :remove-end:
runs = list(
    client.list_runs_from_annotation_queue(queue_id, status="needs_my_review")
)
for run in runs:
    print(run.name)

first_run = client.get_run_from_annotation_queue(queue_id, index=0)
# :snippet-end:

# :remove-start:
assert len(runs) == 1, f"expected 1 run, got {len(runs)}"
assert first_run.id == runs[0].id
print("✓ runs-list-from-queue-before validated")
# :remove-end:


# :snippet-start: runs-list-from-queue-after-py
# :codegroup-tab: After
import asyncio

from langsmith import Client


async def main():
    client = Client()
    queue_id = "<queue-id>"
    # :remove-start:
    queue_id = _seed_queue()
    names = []
    # :remove-end:
    count = await client.annotation_queues.items.retrieve_count(
        queue_id, status="needs_my_review"
    )
    print(count.count)

    # Items carry the run's lookup keys, not its contents.
    async for item in client.annotation_queues.items.list(
        queue_id, status="needs_my_review", item_type="RUN"
    ):
        run = await client.runs.retrieve_v2(
            item.run_id,
            project_id=item.project_id,
            start_time=item.start_time,
            selects=["NAME", "STATUS", "INPUTS", "OUTPUTS"],
        )
        print(run.name, run.status)
        # :remove-start:
        names.append(run.name)
        # :remove-end:
    # :remove-start:
    assert count.count == 1, f"expected count 1, got {count.count}"
    assert len(names) == 1 and names[0], f"expected 1 named run, got {names}"
    # :remove-end:


asyncio.run(main())
# :snippet-end:

# :remove-start:
print("✓ runs-list-from-queue-after validated")
# :remove-end:
