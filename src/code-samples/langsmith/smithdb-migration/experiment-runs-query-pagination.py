# :remove-start:
from langsmith import Client

_setup_client = Client()
_DATASET_NAME = "docs-experiment-runs-query-fixture"
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


def _target(inputs: dict) -> dict:
    a, b = (int(x) for x in inputs["question"].split(" + "))
    return {"answer": str(a + b)}


def correctness(outputs: dict, reference_outputs: dict) -> bool:
    return outputs["answer"] == reference_outputs["answer"]


_results = _setup_client.evaluate(
    _target,
    data=_DATASET_NAME,
    evaluators=[correctness],
    experiment_prefix="docs-experiment-runs-query-pagination",
)
dataset_id = _results.get_dataset_id()
experiment_name = _results.experiment_name
# :remove-end:

# :snippet-start: experiment-runs-query-pagination-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
experiment_id = client.read_project(project_name=experiment_name).id
# get_experiment_results paginated internally; increase `limit` to fetch
# more results in a single call. There is no cursor to pass in manually.
results = client.get_experiment_results(
    project_id=experiment_id,
    limit=100,
)
examples_with_runs = list(results["examples_with_runs"])
# :snippet-end:

# :snippet-start: experiment-runs-query-pagination-after-py
# :codegroup-tab: After
from langsmith import Client
import asyncio


async def main():
    client = Client()
    experiment_id = client.read_project(project_name=experiment_name).id
    page = await client.datasets.experiment_runs.query(
        dataset_id,
        experiment_ids=[experiment_id],
        page_size=1,
    )
    runs = []
    async for run in page:
        runs.append(run)
    return runs


examples_with_runs = asyncio.run(main())
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert len(examples_with_runs) == 3
    print("✓ experiment-runs-query-pagination")
# :remove-end:
