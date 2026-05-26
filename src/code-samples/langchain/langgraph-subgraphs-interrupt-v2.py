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

# Invoke - the subagent's tool calls interrupt()
response = agent.invoke(
    {"messages": [{"role": "user", "content": "Tell me about apples"}]},
    config=config,
    version="v2",
)
# response.interrupts contains pending interrupts

# Resume - approve the interrupt
response = agent.invoke(Command(resume=True), config=config, version="v2")
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "1"}}
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "Tell me about apples"}]},
        config=config,
        version="v2",
    )
    assert response.interrupts
    response = agent.invoke(Command(resume=True), config=config, version="v2")
    assert response.value["messages"]
    print("✓ langgraph-subgraphs-interrupt-v2")
# :remove-end:
