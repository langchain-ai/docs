"""Profiles: plugin entry-point registration callables."""

# :snippet-start: profiles-plugin-register-py
from deepagents import (
    HarnessProfile,
    ProviderProfile,
    register_harness_profile,
    register_provider_profile,
)


def register_harness() -> None:
    register_harness_profile(
        "my_provider",
        HarnessProfile(system_prompt_suffix="Batch independent tool calls in parallel."),
    )


def register_provider() -> None:
    register_provider_profile(
        "my_provider",
        ProviderProfile(init_kwargs={"temperature": 0}),
    )
# :snippet-end:

# :remove-start:
register_harness()
register_provider()
print("✓ profiles-plugin-register sample validated")
# :remove-end:
