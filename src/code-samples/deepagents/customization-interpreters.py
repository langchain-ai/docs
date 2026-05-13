"""Customization: code interpreter middleware example."""

# :remove-start:
from deepagents import create_deep_agent

model = "anthropic:claude-sonnet-4-6"
# :remove-end:

# :snippet-start: customization-interpreters-py
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model=model,
    middleware=[CodeInterpreterMiddleware()],
)
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:
