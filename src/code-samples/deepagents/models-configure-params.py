"""Models: configure model parameters."""

# :snippet-start: models-configure-params-init-chat-model-py
# :codegroup-tab: init_chat_model
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

model = init_chat_model(
    # KEEP MODEL
    model="google_genai:gemini-3.5-flash",
    thinking_level="medium",  # [!code highlight]
)
agent = create_deep_agent(model=model)
# :snippet-end:

# :snippet-start: models-configure-params-provider-package-py
# :codegroup-tab: Provider package
from langchain_google_genai import ChatGoogleGenerativeAI
from deepagents import create_deep_agent

model = ChatGoogleGenerativeAI(
    # KEEP MODEL
    model="gemini-3.1-pro-preview",
    thinking_level="medium",  # [!code highlight]
)
agent = create_deep_agent(model=model)
# :snippet-end:
