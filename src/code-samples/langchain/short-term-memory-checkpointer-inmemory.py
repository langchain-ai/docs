# :snippet-start: short-term-memory-usage-py
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  # [!code highlight]


def get_user_info() -> str:
    """Look up information about the current user."""
    return "No user profile on file."


agent = create_agent(
    model="openai:gpt-5.5",
    tools=[get_user_info],
    checkpointer=InMemorySaver(),  # [!code highlight]
)

thread_config = {"configurable": {"thread_id": "1"}}
response = agent.invoke(
    {"messages": [{"role": "user", "content": "Hi! My name is Bob."}]},
    thread_config,  # [!code highlight]
)["messages"][-1].content

print(response)  # "Hi Bob! Nice to see you here. How are you doing?"

response = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    thread_config,  # [!code highlight]
)["messages"][-1].content

print(response)  # "You are Bob!"
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert response.strip(), "expected non-empty assistant reply on second turn"
    messages = agent.get_state(thread_config).values["messages"]
    human_msgs = [m for m in messages if m.type == "human"]
    assert len(human_msgs) >= 2, "expected two human turns in thread history"
    assert "bob" in response.lower(), "expected assistant to recall the name from the first turn"
    print("✓ checkpointer persists conversation across turns on the same thread_id")
# :remove-end:
