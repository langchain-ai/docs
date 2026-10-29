"""Tracing quickstart app: Anthropic wrapper plus @traceable."""

# :snippet-start: observability-quickstart-app-anthropic-py
# :codegroup-tab: Python
from anthropic import Anthropic
from langsmith.wrappers import wrap_anthropic
from langsmith import traceable

client = wrap_anthropic(Anthropic())  # log every Anthropic call automatically

@traceable(run_type="tool")  # trace this as a tool span
def get_context(question: str) -> str:
    # In a real app, this would query a knowledge base or vector store
    return "LangSmith traces are stored for 14 days on the Developer plan."

@traceable  # capture the full pipeline as a single trace
def assistant(question: str) -> str:
    context = get_context(question)
    response = client.messages.create(
        # KEEP MODEL
        model="claude-sonnet-5-5",
        max_tokens=1024,
        system=f"Answer using the context below.\n\nContext: {context}",
        messages=[{"role": "user", "content": question}],
    )
    return "".join(block.text for block in response.content if block.type == "text")

if __name__ == "__main__":
    print(assistant("How long are LangSmith traces stored?"))
# :snippet-end:
