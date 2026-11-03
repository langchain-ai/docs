"""Profiles: inherit provider defaults and extend a model registration."""

# :snippet-start: profiles-registration-py
from deepagents import HarnessProfile, register_harness_profile

# Set defaults for a hypothetical provider.
register_harness_profile(
    "my_provider",
    HarnessProfile(
        excluded_tools=frozenset({"execute"}),
        system_prompt_suffix="Respond in under 500 words.",
    ),
)

# Override the prompt suffix for one model; inherit the excluded tool.
register_harness_profile(
    "my_provider:my-model:tag",
    HarnessProfile(system_prompt_suffix="Respond in under 100 words."),
)
# :snippet-end:

# :remove-start:
from deepagents.profiles.harness.harness_profiles import _get_harness_profile

profile = _get_harness_profile("my_provider:my-model:tag")
assert profile is not None
assert profile.excluded_tools == frozenset({"execute"})
assert profile.system_prompt_suffix == "Respond in under 100 words."
other = _get_harness_profile("my_provider:another-model")
assert other is not None
assert other.excluded_tools == frozenset({"execute"})
assert other.system_prompt_suffix == "Respond in under 500 words."
# :remove-end:

# :snippet-start: profiles-reregister-harness-py
register_harness_profile(
    "my_provider:my-model:tag",
    HarnessProfile(excluded_tools=frozenset({"grep"})),
)
# :snippet-end:

# :remove-start:
profile = _get_harness_profile("my_provider:my-model:tag")
assert profile is not None
assert profile.excluded_tools == frozenset({"execute", "grep"})
assert profile.system_prompt_suffix == "Respond in under 100 words."
assert _get_harness_profile("my_provider:another-model") == other
print("Profile registration and re-registration examples validated")
# :remove-end:
