# :snippet-start: agent-invocation-thread-id-py
from langchain.agents import create_agent
from langchain.messages import AIMessage
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model=GenericFakeChatModel(
        messages=iter(
            [
                AIMessage(content="First reply about San Francisco."),
                AIMessage(content="Second reply about tomorrow."),
            ]
        )
    ),
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
    # `result` is the second invoke from the snippet above (same thread_id).
    assert (
        result["messages"][-1].content_blocks[0]["text"]
        == "Second reply about tomorrow."
    )
    human_msgs = [m for m in result["messages"] if m.type == "human"]
    assert len(human_msgs) >= 2

    print("✓ thread_id invocation persists conversation across turns")
# :remove-end:
