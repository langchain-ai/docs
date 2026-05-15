# :snippet-start: streaming-agent-progress-py
from itertools import cycle

from langchain.agents import create_agent
from langchain.messages import AIMessage
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model=GenericFakeChatModel(
        messages=cycle([AIMessage(content="Sunny today.")]),
    ),
    tools=[],
    checkpointer=InMemorySaver(),
)
config = {"configurable": {"thread_id": str(uuid7())}}
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    config=config,
    stream_mode="updates",
    version="v2",
):
    if chunk["type"] == "updates":
        for step, data in chunk["data"].items():
            print(f"step: {step}")
            print(f"content: {data['messages'][-1].content_blocks}")
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    chunks = list(
        agent.stream(
            {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
            config={"configurable": {"thread_id": str(uuid7())}},
            stream_mode="updates",
            version="v2",
        )
    )
    assert any(c.get("type") == "updates" for c in chunks), chunks
    print("✓ streaming agent progress (updates, v2) emits update chunks")
# :remove-end:
