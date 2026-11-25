"""Overview: hide default filesystem tools via a harness profile."""

# :snippet-start: overview-excluded-tools-py
from deepagents import HarnessProfile, register_harness_profile

register_harness_profile(
    "anthropic:claude-sonnet-4-6",
    HarnessProfile(
        excluded_tools=frozenset(
            {"ls", "read_file", "write_file", "edit_file", "delete", "glob", "grep"}
        ),
    ),
)
# :snippet-end:

# :remove-start:
print("✓ overview-excluded-tools validated")
# :remove-end:
