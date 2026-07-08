# :remove-start:
if False:
# :remove-end:
    # :snippet-start: experiment-runs-query-basic-before-py
    # :codegroup-tab: Before
    from langsmith import Client


    async def main():
        client = Client()
        results = client.get_experiment_results(
            project_id=experiment_id,
            limit=20,
            preview=True,
        )
        examples_with_runs = list(results["examples_with_runs"])
    # :snippet-end:

# :remove-start:
if False:
# :remove-end:
    # :snippet-start: experiment-runs-query-basic-after-py
    # :codegroup-tab: After
    from langsmith import Client


    async def main():
        client = Client()
        page = await client.datasets.experiment_runs.query(
            dataset_id,
            experiment_ids=[experiment_id],
            page_size=20,
            selects=["ID", "NAME", "STATUS", "INPUTS_PREVIEW", "OUTPUTS_PREVIEW"],
        )
        examples_with_runs = page.items
    # :snippet-end:
