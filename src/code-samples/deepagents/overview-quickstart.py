"""Overview page: minimal get_weather quickstart."""

# :snippet-start: overview-quickstart-py
from deepagents import create_deep_agent


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

# Run the agent
# :remove-start:
assert agent is not None
assert get_weather("sf") == "It's always sunny in sf!"
print("✓ overview-quickstart sample validated")
# :remove-end:
agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)
# :snippet-end:
