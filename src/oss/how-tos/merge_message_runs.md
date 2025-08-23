# How to merge consecutive messages of the same type

Certain models do not support passing in consecutive [messages](/oss/concepts/messages/) of the same type (a.k.a. "runs" of the same message type).

The `merge_message_runs` utility makes it easy to merge consecutive messages of the same type.

### Setup


```python
%pip install -qU langchain-core langchain-anthropic
```

## Basic usage


```python
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    merge_message_runs,
)

messages = [
    SystemMessage("you're a good assistant."),
    SystemMessage("you always respond with a joke."),
    HumanMessage([{"type": "text", "text": "i wonder why it's called langchain"}]),
    HumanMessage("and who is harrison chasing anyways"),
    AIMessage(
        'Well, I guess they thought "WordRope" and "SentenceString" just didn\'t have the same ring to it!'
    ),
    AIMessage("Why, he's probably chasing after the last cup of coffee in the office!"),
]

merged = merge_message_runs(messages)
print("\n\n".join([repr(x) for x in merged]))
```
```output
SystemMessage(content="you're a good assistant.\nyou always respond with a joke.", additional_kwargs={}, response_metadata={})

HumanMessage(content=[{'type': 'text', 'text': "i wonder why it's called langchain"}, 'and who is harrison chasing anyways'], additional_kwargs={}, response_metadata={})

AIMessage(content='Well, I guess they thought "WordRope" and "SentenceString" just didn\'t have the same ring to it!\nWhy, he\'s probably chasing after the last cup of coffee in the office!', additional_kwargs={}, response_metadata={})
```
Notice that if the contents of one of the messages to merge is a list of content blocks then the merged message will have a list of content blocks. And if both messages to merge have string contents then those are concatenated with a newline character.

## Chaining

`merge_message_runs` can be used imperatively (like above) or declaratively, making it easy to compose with other components in a chain:


```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-7-sonnet-20250219", temperature=0)
# Notice we don't pass in messages. This creates
# a RunnableLambda that takes messages as input
merger = merge_message_runs()
chain = merger | llm
chain.invoke(messages)
```



```output
AIMessage(content='\n\nAs for the actual answer, LangChain is named for connecting (chaining) language models together with other components. And Harrison Chase is one of the co-founders of LangChain, not someone being chased! \n\nBut I like to think he\'s running after runaway tokens that escaped from the embedding space. "Come back here, you vectors!"', additional_kwargs={}, response_metadata={'id': 'msg_018MF8xBrM1ztw69XTx3Uxcy', 'model': 'claude-3-7-sonnet-20250219', 'stop_reason': 'end_turn', 'stop_sequence': None, 'usage': {'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'input_tokens': 84, 'output_tokens': 80, 'server_tool_use': None, 'service_tier': 'standard'}, 'model_name': 'claude-3-7-sonnet-20250219'}, id='run--caa1b9d6-a554-40ad-95cd-268938d8223b-0', usage_metadata={'input_tokens': 84, 'output_tokens': 80, 'total_tokens': 164, 'input_token_details': {'cache_read': 0, 'cache_creation': 0}})
```


Looking at the LangSmith trace we can see that before the messages are passed to the model they are merged: https://smith.langchain.com/public/ab558677-cac9-4c59-9066-1ecce5bcd87c/r

Looking at just the merger, we can see that it's a Runnable object that can be invoked like all Runnables:


```python
merger.invoke(messages)
```



```output
[SystemMessage(content="you're a good assistant.\nyou always respond with a joke.", additional_kwargs={}, response_metadata={}),
 HumanMessage(content=[{'type': 'text', 'text': "i wonder why it's called langchain"}, 'and who is harrison chasing anyways'], additional_kwargs={}, response_metadata={}),
 AIMessage(content='Well, I guess they thought "WordRope" and "SentenceString" just didn\'t have the same ring to it!\nWhy, he\'s probably chasing after the last cup of coffee in the office!', additional_kwargs={}, response_metadata={})]
```


`merge_message_runs` can also be placed after a prompt:


```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate(
    [
        ("system", "You're great a {skill}"),
        ("system", "You're also great at explaining things"),
        ("human", "{query}"),
    ]
)
chain = prompt | merger | llm
chain.invoke({"skill": "math", "query": "what's the definition of a convergent series"})
```



```output
AIMessage(content="# Definition of a Convergent Series\n\nA series is a sum of terms in a sequence, typically written as:\n\n$$\\sum_{n=1}^{\\infty} a_n = a_1 + a_2 + a_3 + \\ldots$$\n\nA series is called **convergent** if the sequence of partial sums approaches a finite limit.\n\n## Formal Definition\n\nLet's define the sequence of partial sums:\n$$S_N = \\sum_{n=1}^{N} a_n = a_1 + a_2 + \\ldots + a_N$$\n\nA series $\\sum_{n=1}^{\\infty} a_n$ is convergent if and only if:\n- The limit of the partial sums exists and is finite\n- That is, there exists a finite number $S$ such that $\\lim_{N \\to \\infty} S_N = S$\n\nIf this limit exists, we say the series converges to $S$, and we write:\n$$\\sum_{n=1}^{\\infty} a_n = S$$\n\nIf the limit doesn't exist or is infinite, the series is called divergent.", additional_kwargs={}, response_metadata={'id': 'msg_018ypyi2MTjV6S7jCydSqDn9', 'model': 'claude-3-7-sonnet-20250219', 'stop_reason': 'end_turn', 'stop_sequence': None, 'usage': {'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'input_tokens': 29, 'output_tokens': 273, 'server_tool_use': None, 'service_tier': 'standard'}, 'model_name': 'claude-3-7-sonnet-20250219'}, id='run--5de0ca29-d031-48f7-bc75-671eade20b74-0', usage_metadata={'input_tokens': 29, 'output_tokens': 273, 'total_tokens': 302, 'input_token_details': {'cache_read': 0, 'cache_creation': 0}})
```


[LangSmith Trace](https://smith.langchain.com/public/432150b6-9909-40a7-8ae7-944b7e657438/r/f4ad5fb2-4d38-42a6-b780-25f62617d53f)

## API reference

For a complete description of all arguments head to the [API reference](https://python.langchain.com/api_reference/core/messages/langchain_core.messages.utils.merge_message_runs.html)
