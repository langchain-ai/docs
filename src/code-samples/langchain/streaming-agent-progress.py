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
for chunk in agent.stream(  # [!code highlight]
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    config=config,
    stream_mode="updates",
    version="v2",  # [!code highlight]
):
    if chunk["type"] == "updates":  # [!code highlight]
        for step, data in chunk["data"].items():  # [!code highlight]
            print(f"step: {step}")
            print(f"content: {data['messages'][-1].content_blocks}")
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    stream = agent.stream_events(
        {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
        config={"configurable": {"thread_id": str(uuid7())}},
        version="v3",
    )
    snapshots = list(stream.values)
    stream.output
    assert len(snapshots) > 0, snapshots
    print("✓ streaming agent progress (stream_events v3) emits value snapshots")
# :remove-end:
