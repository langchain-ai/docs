"""Prompt engineering quickstart: create, test, and iterate on a hub prompt."""

# :remove-start:
# CI and local reruns share the hub prompt "prompt-quickstart" with the
# TypeScript siblings. A second push of the same content returns 409
# "Nothing to commit"; treat that as success so the suite stays idempotent.
from langsmith import Client as _LangSmithClient
from langsmith.utils import LangSmithConflictError as _LangSmithConflictError

_orig_push_prompt = _LangSmithClient.push_prompt


def _push_prompt_idempotent(self, *args, **kwargs):
    try:
        return _orig_push_prompt(self, *args, **kwargs)
    except _LangSmithConflictError as exc:
        if "Nothing to commit" not in str(exc):
            raise
        return None


_LangSmithClient.push_prompt = _push_prompt_idempotent
# :remove-end:

# :snippet-start: prompt-engineering-quickstart-create-py
# :codegroup-tab: Python
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate

client = Client()

prompt = ChatPromptTemplate([
    ("system", "You are a helpful chatbot."),
    ("user", "{question}"),
])

client.push_prompt("prompt-quickstart", object=prompt)
# :snippet-end:

# :snippet-start: prompt-engineering-quickstart-test-py
# :codegroup-tab: Python
from langsmith import Client
from openai import OpenAI
from langchain_core.messages import convert_to_openai_messages

client = Client()
oai_client = OpenAI()

prompt = client.pull_prompt("prompt-quickstart")

# Since the prompt only has one variable you could also pass in the value directly
# Equivalent to formatted_prompt = prompt.invoke("What is the color of the sky?")
formatted_prompt = prompt.invoke({"question": "What is the color of the sky?"})

response = oai_client.chat.completions.create(
    # KEEP MODEL
    model="gpt-6.1-sol",
    messages=convert_to_openai_messages(formatted_prompt.messages),
)
# :snippet-end:

# :remove-start:
assert response.choices[0].message.content, "model returned no content"
print("✓ pulled prompt and called the model")
# :remove-end:

# :snippet-start: prompt-engineering-quickstart-iterate-py
# :codegroup-tab: Python
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate

client = Client()

new_prompt = ChatPromptTemplate([
    ("system", "You are a helpful chatbot. Respond in Spanish."),
    ("user", "{question}"),
])

client.push_prompt("prompt-quickstart", object=new_prompt)
# :snippet-end:

# :remove-start:
print("✓ pushed a second commit to prompt-quickstart")
# :remove-end:
