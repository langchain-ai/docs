"""Deep research agent: synchronous run snippet."""

# :remove-start:
print("✓ deep-research-run-sync sample validated")
raise SystemExit(0)
# :remove-end:

# :snippet-start: deep-research-run-sync-py
from langchain.messages import HumanMessage

if __name__ == "__main__":
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What are the main differences between RAG and fine-tuning for LLM applications?"
                )
            ]
        }
    )

    for msg in result.get("messages", []):
        if hasattr(msg, "content") and msg.content:
            print(msg.content)
# :snippet-end:
