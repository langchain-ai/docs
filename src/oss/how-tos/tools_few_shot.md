# How to use few-shot prompting with tool calling

For more complex tool use it's very useful to add [few-shot examples](/oss/concepts/few_shot_prompting/) to the prompt. We can do this by adding `AIMessage`s with `ToolCall`s and corresponding `ToolMessage`s to our prompt.

First let's define our tools and model.


```python
from langchain_core.tools import tool


@tool
def add(a: int, b: int) -> int:
    """Adds a and b."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiplies a and b."""
    return a * b


tools = [add, multiply]
```


```python
import os
from getpass import getpass

from langchain_openai import ChatOpenAI

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)
```

Let's run our model where we can notice that even with some special instructions our model can get tripped up by order of operations. 


```python
llm_with_tools.invoke(
    "Whats 119 times 8 minus 20. Don't do any math yourself, only use tools for math. Respect order of operations"
).tool_calls
```

```output
[{'name': 'Multiply',
  'args': {'a': 119, 'b': 8},
  'id': 'call_T88XN6ECucTgbXXkyDeC2CQj'},
 {'name': 'Add',
  'args': {'a': 952, 'b': -20},
  'id': 'call_licdlmGsRqzup8rhqJSb1yZ4'}]
```

The model shouldn't be trying to add anything yet, since it technically can't know the results of 119 * 8 yet.

By adding a prompt with some examples we can correct this behavior:


```python
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

examples = [
    HumanMessage(
        "What's the product of 317253 and 128472 plus four", name="example_user"
    ),
    AIMessage(
        "",
        name="example_assistant",
        tool_calls=[
            {"name": "Multiply", "args": {"x": 317253, "y": 128472}, "id": "1"}
        ],
    ),
    ToolMessage("16505054784", tool_call_id="1"),
    AIMessage(
        "",
        name="example_assistant",
        tool_calls=[{"name": "Add", "args": {"x": 16505054784, "y": 4}, "id": "2"}],
    ),
    ToolMessage("16505054788", tool_call_id="2"),
    AIMessage(
        "The product of 317253 and 128472 plus four is 16505054788",
        name="example_assistant",
    ),
]

system = """You are bad at math but are an expert at using a calculator. 

Use past tool usage as an example of how to correctly use the tools."""
few_shot_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        *examples,
        ("human", "{query}"),
    ]
)

chain = {"query": RunnablePassthrough()} | few_shot_prompt | llm_with_tools
chain.invoke("Whats 119 times 8 minus 20").tool_calls
```

```output
[{'name': 'Multiply',
  'args': {'a': 119, 'b': 8},
  'id': 'call_9MvuwQqg7dlJupJcoTWiEsDo'}]
```

And we get the correct output this time.

Here's what the [LangSmith trace](https://smith.langchain.com/public/f70550a1-585f-4c9d-a643-13148ab1616f/r) looks like.
