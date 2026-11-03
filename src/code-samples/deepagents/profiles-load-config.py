"""Profiles: load harness profile from a YAML config file."""

# :remove-start:
from pathlib import Path

Path("openai.yaml").write_text(
    """\
base_system_prompt: You are helpful.
system_prompt_suffix: Respond briefly.
excluded_tools:
  - execute
  - grep
excluded_middleware:
  - SummarizationMiddleware
general_purpose_subagent:
  enabled: false
"""
)
# :remove-end:

# :snippet-start: profiles-load-config-py
import yaml
from deepagents import HarnessProfileConfig, register_harness_profile

with open("openai.yaml") as f:
    register_harness_profile(
        "openai",
        HarnessProfileConfig.from_dict(yaml.safe_load(f)),
    )
# :snippet-end:

# :remove-start:
print("✓ profiles-load-config sample validated")
# :remove-end:
