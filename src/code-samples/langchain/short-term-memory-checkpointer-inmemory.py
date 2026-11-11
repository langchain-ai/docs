# :snippet-start: short-term-memory-usage-py
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  # [!code highlight]


def get_user_info() -> str:
    """Look up information about the current user."""
    return "No user profile on file."


agent = create_agent(
    model="openai:gpt-6.1-sol",
    tools=[get_user_info],
    checkpointer=InMemorySaver(),  # [!code highlight]
)
# :remove-start:
# GPT-6.1 Sol tool calling requires the Responses API. Keep the published
# snippet on a routable model string so CodeGroup tabs still expand.
from langchain_openai import ChatOpenAI

agent = create_agent(
    model=ChatOpenAI(model="gpt-6.1-sol", use_responses_api=True),
    tools=[get_user_info],
    checkpointer=InMemorySaver(),
)
# :remove-end:

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
    # Responses API replies may use block lists; prefer `.text` like the TS sample.
    messages = agent.get_state(thread_config).values["messages"]
    text = messages[-1].text
    assert text.strip(), "expected non-empty assistant reply on second turn"
    human_msgs = [m for m in messages if m.type == "human"]
    assert len(human_msgs) >= 2, "expected two human turns in thread history"
    assert "bob" in text.lower(), "expected assistant to recall the name from the first turn"
    print("✓ checkpointer persists conversation across turns on the same thread_id")
# :remove-end:
