# :remove-start:
import uuid
# :remove-end:


# :snippet-start: runs-add-to-queue-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
queue_id = "<queue-id>"
runs = list(client.list_runs(project_name="default", limit=5))
# :remove-start:
queue = client.create_annotation_queue(name=f"docs-smithdb-migration-{uuid.uuid4()}")
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
from langsmith import Client

client = Client()
queue_id = "<queue-id>"
runs = list(client.list_runs(project_name="default", limit=5))
# :remove-start:
queue = client.create_annotation_queue(name=f"docs-smithdb-migration-{uuid.uuid4()}")
queue_id = str(queue.id)
assert len(runs) > 0, "expected at least one run in the 'default' project"
# :remove-end:
client.add_runs_to_annotation_queue(
    queue_id,
    runs=[
        {
            "run_id": run.id,
            "session_id": run.session_id,
            "start_time": run.start_time,
        }
        for run in runs
    ],
)
# :snippet-end:

# :remove-start:
print("✓ runs-add-to-queue-after validated")
# :remove-end:
