"""Async subagents: good and bad subagent descriptions."""

# :snippet-start: async-subagents-descriptions-good-py
# :codegroup-tab: Good
from deepagents import AsyncSubAgent

AsyncSubAgent(
    name="researcher",
    description="Conducts in-depth research using web search. Use for questions requiring multiple searches and synthesis.",
    graph_id="researcher",
)
# :snippet-end:

# :snippet-start: async-subagents-descriptions-bad-py
# :codegroup-tab: Bad
from deepagents import AsyncSubAgent

AsyncSubAgent(
    name="helper",
    description="helps with stuff",
    graph_id="helper",
)
# :snippet-end:

# :remove-start:
print("✓ async-subagents-descriptions sample validated")
# :remove-end:
