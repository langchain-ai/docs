# :snippet-start: agent-invocation-thread-id-py
from langchain.agents import create_agent
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[],
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": str(uuid7())}}

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]},
    config=config,
)

# A follow-up turn on the same conversation: reuse the same thread_id to keep history
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What about tomorrow?"}]},
    config=config,
)
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    last = result["messages"][-1]
    text = last.content_blocks[0]["text"] if last.content_blocks else str(last.content)
    assert text, "expected non-empty final assistant text"
    human_msgs = [m for m in result["messages"] if m.type == "human"]
    assert len(human_msgs) >= 2
    ai_msgs = [m for m in result["messages"] if m.type == "ai"]
    assert len(ai_msgs) >= 2

    print("✓ thread_id invocation persists conversation across turns")
# :remove-end:
