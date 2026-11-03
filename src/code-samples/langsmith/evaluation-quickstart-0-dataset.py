"""Evaluation quickstart, step 3: create the sample dataset.

Runs before evaluation-quickstart-1-eval.py (lexical order within the
"evaluation-quickstart" serial group).
"""

# :remove-start:
from langsmith import Client as _SetupClient

# create_dataset fails on a name that already exists; start each run clean.
_setup_client = _SetupClient()
if _setup_client.has_dataset(dataset_name="Sample dataset"):
    _setup_client.delete_dataset(dataset_name="Sample dataset")
# :remove-end:

# :snippet-start: evaluation-quickstart-dataset-py
# :codegroup-tab: Python
# dataset.py
from langsmith import Client

def main():
    client = Client()

    # Programmatically create a dataset in LangSmith
    dataset = client.create_dataset(
        dataset_name="Sample dataset",
        description="A sample dataset in LangSmith."
    )

    # Create examples
    examples = [
        {
            "inputs": {"question": "Which country is Mount Kilimanjaro located in?"},
            "outputs": {"answer": "Mount Kilimanjaro is located in Tanzania."},
        },
        {
            "inputs": {"question": "What is Earth's lowest point?"},
            "outputs": {"answer": "Earth's lowest point is The Dead Sea."},
        },
    ]

    # Add examples to the dataset
    client.create_examples(dataset_id=dataset.id, examples=examples)
    print("Created dataset:", dataset.name)

if __name__ == "__main__":
    main()
# :snippet-end:
