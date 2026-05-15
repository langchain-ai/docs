# :snippet-start: agent-invocation-thread-and-context-py
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.messages import AIMessage
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver


@dataclass
class Context:
    user_id: str


agent = create_agent(
    model=GenericFakeChatModel(messages=iter([AIMessage(content="ok")])),
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
    assert result["messages"][-1].content_blocks[0]["text"] == "ok"
    print("✓ thread_id and context invoke together without error")
# :remove-end:
