"""Frontend todo list: enable TodoListMiddleware on create_deep_agent."""

# :snippet-start: frontend-todo-list-setup-py
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    middleware=[TodoListMiddleware()],
)
# :snippet-end:

# :remove-start:
assert agent is not None
print("✓ frontend-todo-list-setup sample validated")
# :remove-end:
