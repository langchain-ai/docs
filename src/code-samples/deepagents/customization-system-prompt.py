"""Customization: system prompt example."""

# :snippet-start: customization-system-prompt-py
from deepagents import create_deep_agent

research_instructions = """\
You are an expert researcher. Your job is to conduct \
thorough research, and then write a polished report. \
"""

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt=research_instructions,
)
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:
