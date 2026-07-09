# :remove-start:
if False:
# :remove-end:
    # :snippet-start: experiment-runs-query-sort-after-py
    # :codegroup-tab: After
    from langsmith import Client


    async def main():
        client = Client()
        page = await client.datasets.experiment_runs.query(
            dataset_id,
            experiment_ids=[experiment_id],
            sort={"by": "feedback.correctness", "order": "ASC"},
        )
    # :snippet-end:
