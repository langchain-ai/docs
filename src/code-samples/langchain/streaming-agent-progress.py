# :snippet-start: streaming-agent-progress-py
from langchain.agents import create_agent
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="gpt-5-nano",
    tools=[get_weather],
    checkpointer=InMemorySaver()
)
config = {"configurable": {"thread_id": str(uuid7())}}
stream = agent.stream_events(  # [!code highlight]
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    config=config,
    version="v3",  # [!code highlight]
)
for kind, item in stream.interleave("messages", "tool_calls"):  # [!code highlight]
    if kind == "messages":
        for token in item.text:
            print(token, end="", flush=True)
    elif kind == "tool_calls":
        print(f"\nTool call: {item.tool_name}({item.input})")
        for delta in item.output_deltas:
            print(delta, end="", flush=True)
        print(f"\nTool result: {item.output}")

final_state = stream.output  # [!code highlight]
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    stream = agent.stream_events(
        {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
        config={"configurable": {"thread_id": str(uuid7())}},
        version="v3",
    )
    messages_seen = 0
    tool_calls_seen = 0
    for kind, item in stream.interleave("messages", "tool_calls"):
        if kind == "messages":
            messages_seen += 1
            list(item.text)
        elif kind == "tool_calls":
            tool_calls_seen += 1
            list(item.output_deltas)
    final_state = stream.output
    assert final_state is not None
    assert messages_seen > 0, messages_seen
    print("✓ streaming agent progress (stream_events v3) uses typed projections")
# :remove-end:
