# How to return artifacts from a tool

<Info>
**Prerequisites**

This guide assumes familiarity with the following concepts:

- [ToolMessage](/oss/concepts/messages/#toolmessage)
- [Tools](/oss/concepts/tools)
- [Function/tool calling](/oss/concepts/tool_calling)

</Info>

[Tools](/oss/concepts/tools/) are utilities that can be [called by a model](/oss/concepts/tool_calling/), and whose outputs are designed to be fed back to a model. Sometimes, however, there are artifacts of a tool's execution that we want to make accessible to downstream components in our chain or agent, but that we don't want to expose to the model itself. For example if a tool returns a custom object, a dataframe or an image, we may want to pass some metadata about this output to the model without passing the actual output to the model. At the same time, we may want to be able to access this full output elsewhere, for example in downstream tools.

The Tool and [ToolMessage](https://python.langchain.com/api_reference/core/messages/langchain_core.messages.tool.ToolMessage.html) interfaces make it possible to distinguish between the parts of the tool output meant for the model (this is the ToolMessage.content) and those parts which are meant for use outside the model (ToolMessage.artifact).

<Info>
**Requires ``langchain-core >= 0.2.19``**


This functionality was added in ``langchain-core == 0.2.19``. Please make sure your package is up to date.

</Info>

## Defining the tool

If we want our tool to distinguish between message content and other artifacts, we need to specify `response_format="content_and_artifact"` when defining our tool and make sure that we return a tuple of (content, artifact):


```python
%pip install -qU "langchain-core>=0.2.19"
```


```python
import random
from typing import List, Tuple

from langchain_core.tools import tool


@tool(response_format="content_and_artifact")
def generate_random_ints(min: int, max: int, size: int) -> Tuple[str, List[int]]:
    """Generate size random ints in the range [min, max]."""
    array = [random.randint(min, max) for _ in range(size)]
    content = f"Successfully generated array of {size} random ints in [{min}, {max}]."
    return content, array
```

## Invoking the tool with ToolCall

If we directly invoke our tool with just the tool arguments, you'll notice that we only get back the content part of the Tool output:


```python
generate_random_ints.invoke({"min": 0, "max": 9, "size": 10})
```



```output
'Successfully generated array of 10 random ints in [0, 9].'
```


In order to get back both the content and the artifact, we need to invoke our model with a ToolCall (which is just a dictionary with "name", "args", "id" and "type" keys), which has additional info needed to generate a ToolMessage like the tool call ID:


```python
generate_random_ints.invoke(
    {
        "name": "generate_random_ints",
        "args": {"min": 0, "max": 9, "size": 10},
        "id": "123",  # required
        "type": "tool_call",  # required
    }
)
```



```output
ToolMessage(content='Successfully generated array of 10 random ints in [0, 9].', name='generate_random_ints', tool_call_id='123', artifact=[2, 8, 0, 6, 0, 0, 1, 5, 0, 0])
```


## Using with a model

With a [tool-calling model](/oss/how-to/tool_calling/), we can easily use a model to call our Tool and generate ToolMessages:

<ChatModelTabs
  customVarName="llm"
/>



```python
# | echo: false
# | output: false

from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0)
```


```python
llm_with_tools = llm.bind_tools([generate_random_ints])

ai_msg = llm_with_tools.invoke("generate 6 positive ints less than 25")
ai_msg.tool_calls
```



```output
[{'name': 'generate_random_ints',
  'args': {'min': 1, 'max': 24, 'size': 6},
  'id': 'toolu_01EtALY3Wz1DVYhv1TLvZGvE',
  'type': 'tool_call'}]
```



```python
generate_random_ints.invoke(ai_msg.tool_calls[0])
```



```output
ToolMessage(content='Successfully generated array of 6 random ints in [1, 24].', name='generate_random_ints', tool_call_id='toolu_01EtALY3Wz1DVYhv1TLvZGvE', artifact=[2, 20, 23, 8, 1, 15])
```


If we just pass in the tool call args, we'll only get back the content:


```python
generate_random_ints.invoke(ai_msg.tool_calls[0]["args"])
```



```output
'Successfully generated array of 6 random ints in [1, 24].'
```


If we wanted to declaratively create a chain, we could do this:


```python
from operator import attrgetter

chain = llm_with_tools | attrgetter("tool_calls") | generate_random_ints.map()

chain.invoke("give me a random number between 1 and 5")
```



```output
[ToolMessage(content='Successfully generated array of 1 random ints in [1, 5].', name='generate_random_ints', tool_call_id='toolu_01FwYhnkwDPJPbKdGq4ng6uD', artifact=[5])]
```


## Creating from BaseTool class

If you want to create a BaseTool object directly, instead of decorating a function with `@tool`, you can do so like this:


```python
from langchain_core.tools import BaseTool


class GenerateRandomFloats(BaseTool):
    name: str = "generate_random_floats"
    description: str = "Generate size random floats in the range [min, max]."
    response_format: str = "content_and_artifact"

    ndigits: int = 2

    def _run(self, min: float, max: float, size: int) -> Tuple[str, List[float]]:
        range_ = max - min
        array = [
            round(min + (range_ * random.random()), ndigits=self.ndigits)
            for _ in range(size)
        ]
        content = f"Generated {size} floats in [{min}, {max}], rounded to {self.ndigits} decimals."
        return content, array

    # Optionally define an equivalent async method

    # async def _arun(self, min: float, max: float, size: int) -> Tuple[str, List[float]]:
    #     ...
```


```python
rand_gen = GenerateRandomFloats(ndigits=4)
rand_gen.invoke({"min": 0.1, "max": 3.3333, "size": 3})
```



```output
'Generated 3 floats in [0.1, 3.3333], rounded to 4 decimals.'
```



```python
rand_gen.invoke(
    {
        "name": "generate_random_floats",
        "args": {"min": 0.1, "max": 3.3333, "size": 3},
        "id": "123",
        "type": "tool_call",
    }
)
```



```output
ToolMessage(content='Generated 3 floats in [0.1, 3.3333], rounded to 4 decimals.', name='generate_random_floats', tool_call_id='123', artifact=[1.5789, 2.464, 2.2719])
```
