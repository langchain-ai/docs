"""Customization: harness profiles example."""

# :snippet-start: customization-profiles-py
from deepagents import HarnessProfile, register_harness_profile

# Append a system-prompt suffix whenever gpt-5.4 is selected.
register_harness_profile(
    "openai:gpt-5.4",
    HarnessProfile(system_prompt_suffix="Respond in under 100 words."),
)
# :snippet-end:
