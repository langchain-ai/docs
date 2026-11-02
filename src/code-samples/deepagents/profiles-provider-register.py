"""Profiles: register provider defaults and override one model."""

# :snippet-start: profiles-provider-register-py
from deepagents import ProviderProfile, register_provider_profile

register_provider_profile(
    "my_provider",
    ProviderProfile(init_kwargs={"temperature": 0.7, "timeout": 30}),
)
register_provider_profile(
    "my_provider:my-model:tag",
    ProviderProfile(init_kwargs={"temperature": 0}),
)
# :snippet-end:

# :remove-start:
from deepagents.profiles.provider.provider_profiles import apply_provider_profile

assert apply_provider_profile("my_provider:my-model:tag") == {
    "temperature": 0,
    "timeout": 30,
}
assert apply_provider_profile("my_provider:another-model") == {
    "temperature": 0.7,
    "timeout": 30,
}
# :remove-end:

# :snippet-start: profiles-reregister-provider-py
register_provider_profile(
    "my_provider:my-model:tag",
    ProviderProfile(init_kwargs={"timeout": 60}),
)
# :snippet-end:

# :remove-start:
assert apply_provider_profile("my_provider:my-model:tag") == {
    "temperature": 0,
    "timeout": 60,
}
assert apply_provider_profile("my_provider:another-model") == {
    "temperature": 0.7,
    "timeout": 30,
}
print("Provider registration and re-registration examples validated")
# :remove-end:
