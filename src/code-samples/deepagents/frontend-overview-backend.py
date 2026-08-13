"""Frontend overview: coordinator-worker backend setup."""


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return "It's always sunny in San Francisco."


# :snippet-start: frontend-overview-backend-py
from deepagents import create_deep_agent

agent = create_deep_agent(
    # KEEP MODEL
    model="google_genai:gemini-3.5-flash",
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
    subagents=[
        {
            "name": "researcher",
            "description": "Research assistant",
            "system_prompt": "You are a research assistant.",
        }
    ],
)
# :snippet-end:
