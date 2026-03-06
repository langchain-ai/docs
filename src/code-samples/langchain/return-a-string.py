# :snippet-start: tool-return-values-py
from langchain.tools import tool


@tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"It is currently sunny in {city}."


# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    result = get_weather.invoke({"city": "San Francisco"})
    assert result == "It is currently sunny in San Francisco."
    print("✓ Tool works as expected")
# :remove-end:
