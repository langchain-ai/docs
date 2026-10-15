"""Deep Agents RAG tutorial: baseline agent without retrieval."""

# :remove-start:
import os
import sys

if not os.environ.get("ANTHROPIC_API_KEY"):
    print("[rag-deep-baseline] Skipping (ANTHROPIC_API_KEY required).")
    sys.exit(0)
# :remove-end:

# :snippet-start: rag-deep-baseline-py
from deepagents import create_deep_agent
from langchain.messages import HumanMessage

EXAMPLE_QUERY = "How do I stream intermediate tool results from a subagent?"

baseline_agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[],
    system_prompt=(
        "You are a helpful LangChain documentation assistant. "
        "Answer questions about LangChain APIs and patterns."
    ),
)

result = baseline_agent.invoke(
    {"messages": [HumanMessage(content=EXAMPLE_QUERY)]}
)

print(result["messages"][-1].text)
# :snippet-end:

# :remove-start:
assert result["messages"][-1].text
print("✓ rag-deep-baseline")
# :remove-end:
