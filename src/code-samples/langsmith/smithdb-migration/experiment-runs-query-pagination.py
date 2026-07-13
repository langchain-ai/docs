# :remove-start:
if False:
# :remove-end:
    # :snippet-start: experiment-runs-query-pagination-before-py
    # :codegroup-tab: Before
    from langsmith import Client


    async def main():
        client = Client()
        # get_experiment_results paginated internally; increase `limit` to fetch
        # more results in a single call. There is no cursor to pass in manually.
        results = client.get_experiment_results(
            project_id=experiment_id,
            limit=100,
        )
        examples_with_runs = list(results["examples_with_runs"])
    # :snippet-end:

# :remove-start:
if False:
# :remove-end:
    # :snippet-start: experiment-runs-query-pagination-after-py
    # :codegroup-tab: After
    from langsmith import Client


    async def main():
        client = Client()
        page = await client.datasets.experiment_runs.query(
            dataset_id,
            experiment_ids=[experiment_id],
            page_size=20,
        )
        async for run in page:
            pass
    # :snippet-end:
