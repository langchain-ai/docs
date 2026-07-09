"""Profiles: register a harness profile."""

# :snippet-start: profiles-harness-register-py
from deepagents import (
    GeneralPurposeSubagentProfile,
    HarnessProfile,
    register_harness_profile,
)

register_harness_profile(
    "openai:gpt-5.5",
    HarnessProfile(
        system_prompt_suffix="Respond in under 100 words.",
        excluded_tools={"execute"},
        excluded_middleware={"SummarizationMiddleware"},
        general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False),
    ),
)
# :snippet-end:

# :remove-start:
print("✓ profiles-harness-register sample validated")
# :remove-end:
