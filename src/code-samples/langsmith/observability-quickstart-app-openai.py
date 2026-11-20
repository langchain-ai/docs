"""Tracing quickstart app: OpenAI wrapper plus @traceable."""

# :snippet-start: observability-quickstart-app-openai-py
# :codegroup-tab: Python
from openai import OpenAI
from langsmith.wrappers import wrap_openai
from langsmith import traceable

client = wrap_openai(OpenAI())  # log every OpenAI call automatically

@traceable(run_type="tool")  # trace this as a tool span
def get_context(question: str) -> str:
    # In a real app, this would query a knowledge base or vector store
    return "LangSmith traces are stored for 14 days on the Developer plan."

@traceable  # capture the full pipeline as a single trace
def assistant(question: str) -> str:
    context = get_context(question)
    response = client.chat.completions.create(
        # KEEP MODEL
        model="gpt-6-luna",
        messages=[
            {
                "role": "system",
                "content": f"Answer using the context below.\n\nContext: {context}",
            },
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print(assistant("How long are LangSmith traces stored?"))
# :snippet-end:
