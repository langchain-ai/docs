"""Integration testing: cap max tokens on the chat model."""

# :remove-start:
import os

from langchain.tools import tool

os.environ.setdefault("GOOGLE_API_KEY", "test-key")
os.environ.setdefault("GEMINI_API_KEY", "test-key")


@tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"It is sunny in {city}."


# :remove-end:
# :snippet-start: integration-testing-max-tokens-py
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

model = init_chat_model("google_genai:gemini-3.1-flash-lite", max_tokens=256)

agent = create_agent(model, tools=[get_weather])
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    expected_max_tokens = 256
    assert model.max_output_tokens == expected_max_tokens
    assert agent is not None
    print("✓ integration-testing-max-tokens validated")
# :remove-end:
