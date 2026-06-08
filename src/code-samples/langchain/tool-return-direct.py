# :snippet-start: tool-return-direct-py
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI


@tool(return_direct=True)
def fetch_order_status(order_id: str) -> str:
    """Fetch the current status of a customer order."""
    # In production, query your order management system here
    return f"Order {order_id} is shipped and will arrive in 2 days."


agent = create_agent(
    ChatOpenAI(model="gpt-4o-mini"),
    tools=[fetch_order_status],
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What is the status of order #12345?"}]
})
# The agent returns the tool output directly without another LLM call:
# "Order 12345 is shipped and will arrive in 2 days."
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    last = result["messages"][-1]
    text = (
        last.content_blocks[0]["text"]
        if getattr(last, "content_blocks", None)
        else str(last.content)
    )

    assert "shipped" in text and "12345" in text, text
    print("✓ returnDirect tool sample completed")
# :remove-end:
