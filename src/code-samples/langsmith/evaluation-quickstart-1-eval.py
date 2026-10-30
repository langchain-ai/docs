"""Evaluation quickstart, steps 4 to 6: target, evaluator, and evaluate().

The page shows one growing eval.py three times. Each snippet below is the
file at that step; Python lets the later definitions replace the earlier
ones, and only the last snippet calls main().
"""

# :snippet-start: evaluation-quickstart-eval-target-py
# :codegroup-tab: Python
# eval.py
from langsmith import Client, wrappers
from openai import OpenAI

# Wrap the OpenAI client for LangSmith tracing
openai_client = wrappers.wrap_openai(OpenAI())

# Define the application logic you want to evaluate inside a target function
# The SDK will automatically send the inputs from the dataset to your target function
def target(inputs: dict) -> dict:
    response = openai_client.chat.completions.create(
        # KEEP MODEL
        model="gpt-6-luna",
        messages=[
            {"role": "system", "content": "Answer the following question accurately"},
            {"role": "user", "content": inputs["question"]},
        ],
    )
    return {"answer": response.choices[0].message.content.strip()}
# :snippet-end:

# :snippet-start: evaluation-quickstart-eval-evaluator-py
# :codegroup-tab: Python
# :codegroup-fence-mods: highlight={3,4,21-31}
from langsmith import Client, wrappers
from openai import OpenAI
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

# Wrap the OpenAI client for LangSmith tracing
openai_client = wrappers.wrap_openai(OpenAI())

# Define the application logic you want to evaluate inside a target function
# The SDK will automatically send the inputs from the dataset to your target function
def target(inputs: dict) -> dict:
    response = openai_client.chat.completions.create(
        # KEEP MODEL
        model="gpt-6-luna",
        messages=[
            {"role": "system", "content": "Answer the following question accurately"},
            {"role": "user", "content": inputs["question"]},
        ],
    )
    return {"answer": response.choices[0].message.content.strip()}

def correctness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    evaluator = create_llm_as_judge(
        prompt=CORRECTNESS_PROMPT,
        # KEEP MODEL
        model="openai:gpt-5.5",
        feedback_key="correctness",
    )
    return evaluator(
        inputs=inputs,
        outputs=outputs,
        reference_outputs=reference_outputs
    )
# :snippet-end:

# :snippet-start: evaluation-quickstart-eval-run-py
# :codegroup-tab: Python
# :codegroup-fence-mods: highlight={33-49}
from langsmith import Client, wrappers
from openai import OpenAI
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

# Wrap the OpenAI client for LangSmith tracing
openai_client = wrappers.wrap_openai(OpenAI())

# Define the application logic you want to evaluate inside a target function
# The SDK will automatically send the inputs from the dataset to your target function
def target(inputs: dict) -> dict:
    response = openai_client.chat.completions.create(
        # KEEP MODEL
        model="gpt-6-luna",
        messages=[
            {"role": "system", "content": "Answer the following question accurately"},
            {"role": "user", "content": inputs["question"]},
        ],
    )
    return {"answer": response.choices[0].message.content.strip()}

def correctness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    evaluator = create_llm_as_judge(
        prompt=CORRECTNESS_PROMPT,
        # KEEP MODEL
        model="openai:gpt-5.5",
        feedback_key="correctness",
    )
    return evaluator(
        inputs=inputs,
        outputs=outputs,
        reference_outputs=reference_outputs
    )

# After running the evaluation, a link will be provided to view the results in langsmith
def main():
    client = Client()
    experiment_results = client.evaluate(
        target,
        data="Sample dataset",
        evaluators=[
            correctness_evaluator,
            # can add multiple evaluators here
        ],
        experiment_prefix="first-eval-in-langsmith",
        max_concurrency=2,
    )
    print(experiment_results)

if __name__ == "__main__":
    main()
# :snippet-end:
