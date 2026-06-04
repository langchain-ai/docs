# :snippet-start: agent-invocation-thread-and-context-py
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain_core.utils.uuid import uuid7
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver


@dataclass
class Context:
    user_id: str


agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[],
    context_schema=Context,
    checkpointer=InMemorySaver(),
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]},
    config={"configurable": {"thread_id": str(uuid7())}},
    context=Context(user_id="user-123"),
)
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    last = result["messages"][-1]
    text = last.content_blocks[0]["text"] if last.content_blocks else str(last.content)
    assert text.strip(), "expected non-empty assistant reply"
    print("✓ thread_id and context invoke together without error")
# :remove-end:
