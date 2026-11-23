"""Models: init_chat_model with a custom OpenAI-compatible base URL."""

# :remove-start:
import os

os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")
# :remove-end:

# :snippet-start: models-init-chat-openai-compatible-py
from langchain.chat_models import init_chat_model

model = init_chat_model(
    model="gpt-5.4-mini",
    model_provider="openai",
    base_url="https://api.openai.com/v1",
    api_key=os.environ["OPENAI_API_KEY"],
)
# :snippet-end:

# :remove-start:
assert model is not None
print("✓ models-init-chat-openai-compatible validated")
# :remove-end:
