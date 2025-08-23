---
sidebar_position: 2
---

# How to add default invocation args to a Runnable

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:
- [LangChain Expression Language (LCEL)](/oss/concepts/lcel)
- [Chaining runnables](/oss/how-to/sequence/)
- [Tool calling](/oss/how-to/tool_calling)

</Info>

Sometimes we want to invoke a [`Runnable`](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.base.Runnable.html) within a [RunnableSequence](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.base.RunnableSequence.html) with constant arguments that are not part of the output of the preceding Runnable in the sequence, and which are not part of the user input. We can use the [`Runnable.bind()`](https://python.langchain.com/api_reference/langchain_core/runnables/langchain_core.runnables.base.Runnable.html#langchain_core.runnables.base.Runnable.bind) method to set these arguments ahead of time.

## Binding stop sequences

Suppose we have a simple prompt + model chain:


```python
# | output: false
# | echo: false

%pip install -qU langchain langchain_openai

import os
from getpass import getpass

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass()
```


```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Write out the following equation using algebraic symbols then solve it. Use the format\n\nEQUATION:...\nSOLUTION:...\n\n",
        ),
        ("human", "{equation_statement}"),
    ]
)

model = ChatOpenAI(temperature=0)

runnable = (
    {"equation_statement": RunnablePassthrough()} | prompt | model | StrOutputParser()
)

print(runnable.invoke("x raised to the third plus seven equals 12"))
```
```output
EQUATION: x^3 + 7 = 12

SOLUTION: 
Subtract 7 from both sides:
x^3 = 5

Take the cube root of both sides:
x = ∛5
```
and want to call the model with certain `stop` words so that we shorten the output as is useful in certain types of prompting techniques. While we can pass some arguments into the constructor, other runtime args use the `.bind()` method as follows:


```python
runnable = (
    {"equation_statement": RunnablePassthrough()}
    | prompt
    | model.bind(stop="SOLUTION")
    | StrOutputParser()
)

print(runnable.invoke("x raised to the third plus seven equals 12"))
```
```output
EQUATION: x^3 + 7 = 12
```
What you can bind to a Runnable will depend on the extra parameters you can pass when invoking it.

## Attaching OpenAI tools

Another common use-case is tool calling. While you should generally use the [`.bind_tools()`](/oss/how-to/tool_calling) method for tool-calling models, you can also bind provider-specific args directly if you want lower level control:


```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]
```


```python
model = ChatOpenAI(model="gpt-4o-mini").bind(tools=tools)
model.invoke("What's the weather in SF, NYC and LA?")
```



```output
AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_z0OU2CytqENVrRTI6T8DkI3u', 'function': {'arguments': '{"location": "San Francisco, CA", "unit": "celsius"}', 'name': 'get_current_weather'}, 'type': 'function'}, {'id': 'call_ft96IJBh0cMKkQWrZjNg4bsw', 'function': {'arguments': '{"location": "New York, NY", "unit": "celsius"}', 'name': 'get_current_weather'}, 'type': 'function'}, {'id': 'call_tfbtGgCLmuBuWgZLvpPwvUMH', 'function': {'arguments': '{"location": "Los Angeles, CA", "unit": "celsius"}', 'name': 'get_current_weather'}, 'type': 'function'}]}, response_metadata={'token_usage': {'completion_tokens': 84, 'prompt_tokens': 85, 'total_tokens': 169}, 'model_name': 'gpt-4o-mini', 'system_fingerprint': 'fp_77a673219d', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-d57ad5fa-b52a-4822-bc3e-74f838697e18-0', tool_calls=[{'name': 'get_current_weather', 'args': {'location': 'San Francisco, CA', 'unit': 'celsius'}, 'id': 'call_z0OU2CytqENVrRTI6T8DkI3u'}, {'name': 'get_current_weather', 'args': {'location': 'New York, NY', 'unit': 'celsius'}, 'id': 'call_ft96IJBh0cMKkQWrZjNg4bsw'}, {'name': 'get_current_weather', 'args': {'location': 'Los Angeles, CA', 'unit': 'celsius'}, 'id': 'call_tfbtGgCLmuBuWgZLvpPwvUMH'}])
```


## Next steps

You now know how to bind runtime arguments to a Runnable.

To learn more, see the other how-to guides on runnables in this section, including:

- [Using configurable fields and alternatives](/oss/how-to/configure) to change parameters of a step in a chain, or even swap out entire steps, at runtime
