# :remove-start:
import uuid
from datetime import datetime, timezone

from langsmith import Client

_setup_client = Client()
_DATASET_NAME = "docs-experiment-runs-query-fixture"
_EXPERIMENT_NAME = "docs-experiment-runs-query-fixture-experiment"

if not _setup_client.has_dataset(dataset_name=_DATASET_NAME):
    _dataset = _setup_client.create_dataset(dataset_name=_DATASET_NAME)
    _setup_client.create_examples(
        dataset_id=_dataset.id,
        examples=[
            {"inputs": {"question": "2 + 2"}, "outputs": {"answer": "4"}},
            {"inputs": {"question": "3 + 3"}, "outputs": {"answer": "6"}},
            {"inputs": {"question": "4 + 4"}, "outputs": {"answer": "9"}},
        ],
    )
dataset_id = _setup_client.read_dataset(dataset_name=_DATASET_NAME).id

# The experiment is shared across every experiment-runs-query sample (this
# file and its siblings): created once, ever, and reused afterward so the
# suite doesn't spend a real evaluation run per file.
if not _setup_client.has_project(_EXPERIMENT_NAME):
    _setup_client.create_project(
        project_name=_EXPERIMENT_NAME, reference_dataset_id=dataset_id
    )
    for _example in _setup_client.list_examples(dataset_id=dataset_id):
        _a, _b = (int(x) for x in _example.inputs["question"].split(" + "))
        _answer = str(_a + _b)
        _run_id = str(uuid.uuid4())
        _now = datetime.now(timezone.utc)
        _setup_client.create_run(
            name="target",
            inputs=_example.inputs,
            run_type="chain",
            id=_run_id,
            outputs={"answer": _answer},
            reference_example_id=_example.id,
            project_name=_EXPERIMENT_NAME,
            start_time=_now,
            end_time=_now,
        )
        _score = 1 if _answer == _example.outputs["answer"] else 0
        _setup_client.create_feedback(_run_id, "correctness", score=_score)
    # Sorting queries derive their time window from the experiment's start
    # time, truncated to whole seconds server-side. A short buffer avoids a
    # same-second min/max window on whichever run performs this creation.
    import time as _time

    _time.sleep(1)

experiment_name = _EXPERIMENT_NAME
# :remove-end:

# :snippet-start: experiment-runs-query-sort-after-py
# :codegroup-tab: After
from langsmith import Client
import asyncio


async def main():
    client = Client()
    experiment_id = client.read_project(project_name=experiment_name).id
    page = await client.datasets.experiment_runs.query(
        str(dataset_id),
        experiment_ids=[str(experiment_id)],
        sort={"by": "feedback.correctness", "order": "ASC"},
    )
    return page.items


examples_with_runs = asyncio.run(main())
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert len(examples_with_runs) == 3
    print("✓ experiment-runs-query-sort")
# :remove-end:
