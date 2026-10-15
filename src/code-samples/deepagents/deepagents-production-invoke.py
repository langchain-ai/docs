# :snippet-start: deepagents-production-invoke-py
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain_core.utils.uuid import uuid7


@dataclass
class Context:
    user_id: str


agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    context_schema=Context,
)

# Start a conversation
config = {"configurable": {"thread_id": str(uuid7())}}
agent.invoke(
    {"messages": [{"role": "user", "content": "Plan a 3-day trip to Tokyo"}]},
    config=config,
    context=Context(user_id="user-123"),
)

# Follow-up on the same conversation: reuse the same thread_id
agent.invoke(
    {"messages": [{"role": "user", "content": "Make it 5 days instead"}]},
    config=config,
    context=Context(user_id="user-123"),
)
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert agent is not None
    print("✓ deep agent production invoke sample completed")
# :remove-end:
