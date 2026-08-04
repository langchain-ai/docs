# :snippet-start: feedback-create-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
run_id = "<run-id>"
# :remove-start:
project = client.read_project(project_name="default")
runs = list(client.list_runs(project_name="default", limit=1))
assert len(runs) > 0, "expected at least one run in the 'default' project"
run_id = str(runs[0].id)
# :remove-end:
client.create_feedback(
    run_id=run_id,
    key="user_feedback",
    score=1,
)
# :snippet-end:

# :remove-start:
print("✓ feedback-create-before validated")
# :remove-end:


# :snippet-start: feedback-create-after-py
# :codegroup-tab: After
from langsmith import Client

client = Client()
run_id = "<run-id>"
session_id = "<session-id>"
# :remove-start:
project = client.read_project(project_name="default")
session_id = str(project.id)
runs = list(client.list_runs(project_name="default", limit=1))
assert len(runs) > 0, "expected at least one run in the 'default' project"
run_id = str(runs[0].id)
# :remove-end:
client.create_feedback(
    run_id=run_id,
    key="user_feedback",
    score=1,
    session_id=session_id,
)
# :snippet-end:

# :remove-start:
print("✓ feedback-create-after validated")
# :remove-end:
