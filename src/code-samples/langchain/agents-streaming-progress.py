from langchain.agents import create_agent
from langchain.tools import tool
# :snippet-start: agents-streaming-progress-py
from langchain.messages import AIMessage, HumanMessage

# :remove-start:
@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"


agent = create_agent(
    model="openai:gpt-5.4",
    tools=[search],
)
# :remove-end:

stream = agent.stream_events(
    {"messages": [{"role": "user", "content": "Search for AI news and summarize the findings"}]},
    version="v3",
)
for snapshot in stream.values:
    # Each snapshot contains the full state at that point
    latest_message = snapshot["messages"][-1]
    if latest_message.content:
        if isinstance(latest_message, HumanMessage):
            print(f"User: {latest_message.content}")
        elif isinstance(latest_message, AIMessage):
            print(f"Agent: {latest_message.content}")
    elif latest_message.tool_calls:
        print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    test_stream = agent.stream_events(
        {"messages": [{"role": "user", "content": "Search for AI news and summarize the findings"}]},
        version="v3",
    )
    snapshots = list(test_stream.values)
    test_stream.output
    assert len(snapshots) > 0, snapshots
    print("✓ agents streaming progress (stream_events v3) emits value snapshots")
# :remove-end:
