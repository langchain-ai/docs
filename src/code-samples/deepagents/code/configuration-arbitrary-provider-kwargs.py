"""Configuration: arbitrary provider model constructor kwargs example."""

# :remove-start:
class MyChatModel:
    """Stub for docs illustration."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs


# :remove-end:

# :snippet-start: configuration-arbitrary-provider-kwargs-py
MyChatModel(model="my-model-v1", base_url="...", api_key="...", temperature=0, max_tokens=4096)
# :snippet-end:

# :remove-start:
model = MyChatModel(
    model="my-model-v1",
    base_url="...",
    api_key="...",
    temperature=0,
    max_tokens=4096,
)
assert model.kwargs["model"] == "my-model-v1"
assert model.kwargs["temperature"] == 0
print("✓ configuration-arbitrary-provider-kwargs sample validated")
# :remove-end:
