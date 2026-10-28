"""LLM Gateway quickstart: one chat completions call through the gateway."""

# :remove-start:
import os as _os

# CI holds the gateway key as LS_GATEWAY_KEY; the docs read LANGSMITH_API_KEY.
if _os.environ.get("LS_GATEWAY_KEY"):
    _os.environ["LANGSMITH_API_KEY"] = _os.environ["LS_GATEWAY_KEY"]
# :remove-end:

# :snippet-start: llm-gateway-quickstart-chat-py
# :codegroup-tab: Python
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://gateway.smith.langchain.com/v1",
    api_key=os.environ["LANGSMITH_API_KEY"],
)
response = client.chat.completions.create(
    # KEEP MODEL
    model="anthropic/claude-opus-5",
    messages=[{"role": "user", "content": "Explain what an LLM gateway does in one sentence."}],
)
print(response.choices[0].message.content)
# :snippet-end:
