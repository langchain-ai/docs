# :remove-start:
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt


@tool
def fruit_info(fruit_name: str) -> str:
    """Look up fruit info."""
    interrupt("continue?")
    return f"Info about {fruit_name}"


agent = create_agent(
    model="gpt-5-nano",
    tools=[fruit_info],
    system_prompt="You are a fruit expert. Use the fruit_info tool for every fruit question.",
    checkpointer=MemorySaver(),
)
# :remove-end:

# :snippet-start: langgraph-subgraphs-interrupt-v2-py
from langgraph.types import Command

config = {"configurable": {"thread_id": "1"}}

# Stream events - the subagent's tool calls interrupt()
stream = agent.stream_events(
    {"messages": [{"role": "user", "content": "Tell me about apples"}]},
    config=config,
    version="v3",
)
output = stream.output  # drive the stream to completion
# stream.interrupts contains pending interrupts (and stream.interrupted is True)

# Resume - approve the interrupt
resumed = agent.stream_events(Command(resume=True), config=config, version="v3")
final = resumed.output
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert stream.interrupted
    assert resumed.output["messages"]
    print("✓ langgraph-subgraphs-interrupt-v2")
# :remove-end:
