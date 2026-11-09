"""Prebuilt middleware: SubAgentMiddleware examples."""

# :remove-start:
import os

os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-key")
# :remove-end:

# :snippet-start: middleware-subagent-py
from deepagents.backends import StateBackend
from deepagents.middleware.subagents import SubAgentMiddleware
from langchain.agents import create_agent
from langchain.tools import tool


@tool
def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."


agent = create_agent(
    model="claude-sonnet-4-6",
    middleware=[
        SubAgentMiddleware(
            backend=StateBackend(),
            subagents=[
                {
                    "name": "weather",
                    "description": "This subagent can get weather in cities.",
                    "system_prompt": (
                        "Use the get_weather tool to get the weather in a city."
                    ),
                    "tools": [get_weather],
                    "model": "gpt-5.5",
                    "middleware": [],
                }
            ],
        )
    ],
)
# :snippet-end:

# :remove-start:
assert agent is not None
_declarative_agent = agent
# :remove-end:

# :snippet-start: middleware-subagent-compiled-py
from deepagents import CompiledSubAgent
from deepagents.backends import StateBackend
from deepagents.middleware.subagents import SubAgentMiddleware
from langchain.agents import create_agent
from langchain.messages import AIMessage
from langgraph.graph import END, START, MessagesState, StateGraph


# Create a custom LangGraph graph
def create_weather_graph():
    workflow = StateGraph(MessagesState)

    def respond(_state: MessagesState):
        return {"messages": [AIMessage(content="The weather is sunny.")]}

    workflow.add_node("respond", respond)
    workflow.add_edge(START, "respond")
    workflow.add_edge("respond", END)
    return workflow.compile()


weather_graph = create_weather_graph()

# Wrap it in a CompiledSubAgent
weather_subagent = CompiledSubAgent(
    name="weather",
    description="This subagent can get weather in cities.",
    runnable=weather_graph,
)

agent = create_agent(
    model="claude-sonnet-4-6",
    middleware=[
        SubAgentMiddleware(
            backend=StateBackend(),
            subagents=[weather_subagent],
        )
    ],
)
# :snippet-end:

# :remove-start:
assert agent is not None
assert _declarative_agent is not None
print("✓ middleware-subagent validated")
# :remove-end:
