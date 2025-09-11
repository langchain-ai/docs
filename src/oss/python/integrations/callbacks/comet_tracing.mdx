---
title: Comet Tracing
---

There are two ways to trace your LangChains executions with Comet:

1. Setting the `LANGCHAIN_COMET_TRACING` environment variable to "true". This is the recommended way.
2. Import the `CometTracer` manually and pass it explicitely.

```python
import os

import comet_llm
from langchain_openai import OpenAI

os.environ["LANGCHAIN_COMET_TRACING"] = "true"

# Connect to Comet if no API Key is set
comet_llm.init()

# comet documentation to configure comet using env variables
# https://www.comet.com/docs/v2/api-and-sdk/llm-sdk/configuration/
# here we are configuring the comet project
os.environ["COMET_PROJECT_NAME"] = "comet-example-langchain-tracing"

from langchain.agents import AgentType, initialize_agent, load_tools
```

```python
# Agent run with tracing. Ensure that OPENAI_API_KEY is set appropriately to run this example.

llm = OpenAI(temperature=0)
tools = load_tools(["llm-math"], llm=llm)
```

```python
agent = initialize_agent(
    tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)

agent.run("What is 2 raised to .123243 power?")  # this should be traced
# An url for the chain like the following should print in your console:
# https://www.comet.com/<workspace>/<project_name>
# The url can be used to view the LLM chain in Comet.
```

```python
# Now, we unset the environment variable and use a context manager.
if "LANGCHAIN_COMET_TRACING" in os.environ:
    del os.environ["LANGCHAIN_COMET_TRACING"]

from langchain_community.callbacks.tracers.comet import CometTracer

tracer = CometTracer()

# Recreate the LLM, tools and agent and passing the callback to each of them
llm = OpenAI(temperature=0)
tools = load_tools(["llm-math"], llm=llm)
agent = initialize_agent(
    tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)

agent.run(
    "What is 2 raised to .123243 power?", callbacks=[tracer]
)  # this should be traced
```
