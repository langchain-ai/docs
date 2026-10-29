"""Prompt engineering quickstart: create, test, and iterate on a hub prompt."""

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
    model="gpt-5.5",
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
