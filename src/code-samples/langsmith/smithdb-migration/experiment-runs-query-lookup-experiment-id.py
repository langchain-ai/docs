# :remove-start:
if False:
# :remove-end:
    # :snippet-start: experiment-runs-query-lookup-experiment-id-py
    from langsmith import Client

    client = Client()
    experiment_id = client.read_project(project_name="my-experiment").id
    # :snippet-end:
