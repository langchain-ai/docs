"""Profiles: register a provider profile."""

# :snippet-start: profiles-provider-register-py
from deepagents import ProviderProfile, register_provider_profile

register_provider_profile(
    "openai",
    ProviderProfile(init_kwargs={"temperature": 0}),
)
# :snippet-end:

# :remove-start:
print("✓ profiles-provider-register sample validated")
# :remove-end:
