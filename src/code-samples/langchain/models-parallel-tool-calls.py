"""Models: disable parallel tool calls."""

# :remove-start:
import os

os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")

from langchain.tools import tool
from langchain_openai import ChatOpenAI


@tool
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"Weather in {city} is sunny"


model = ChatOpenAI(model="gpt-5.4-mini")
# :remove-end:

# :snippet-start: models-parallel-tool-calls-py
model.bind_tools([get_weather], parallel_tool_calls=False)
# :snippet-end:

# :remove-start:
bound = model.bind_tools([get_weather], parallel_tool_calls=False)
assert bound is not None
print("✓ models-parallel-tool-calls validated")
# :remove-end:
