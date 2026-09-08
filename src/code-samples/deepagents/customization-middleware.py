"""Customization: custom middleware example."""

# :snippet-start: customization-middleware-py
from langchain.agents.middleware import wrap_tool_call
from langchain.tools import tool
from deepagents import create_deep_agent


@tool
def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."


call_count = [0]  # Use list to allow modification in nested function


@wrap_tool_call
def log_tool_calls(request, handler):
    """Intercept and log every tool call - demonstrates cross-cutting concern."""
    call_count[0] += 1
    tool_name = request.name if hasattr(request, "name") else str(request)

    print(f"[Middleware] Tool call #{call_count[0]}: {tool_name}")
    print(f"[Middleware] Arguments: {request.args if hasattr(request, 'args') else 'N/A'}")

    # Execute the tool call
    result = handler(request)

    # Log the result
    print(f"[Middleware] Tool call #{call_count[0]} completed")

    return result


agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[get_weather],
    middleware=[log_tool_calls],
)
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:

# :snippet-start: customization-middleware-do-py
from langchain.agents.middleware import AgentMiddleware


class CustomMiddleware(AgentMiddleware):
    def __init__(self):
        pass

    def before_agent(self, state, runtime):
        return {"x": state.get("x", 0) + 1}  # Update graph state instead


# :snippet-end:

# :snippet-start: customization-middleware-dont-py
class CustomMiddlewareBad(AgentMiddleware):
    def __init__(self):
        self.x = 1

    def before_agent(self, state, runtime):
        self.x += 1  # Mutation causes race conditions


# :snippet-end:
