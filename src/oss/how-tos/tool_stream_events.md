# How to stream events from a tool

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:
- [LangChain Tools](/oss/concepts/tools)
- [Custom tools](/oss/how-to/custom_tools)
- [Using stream events](/oss/how-to/streaming/#using-stream-events)
- [Accessing RunnableConfig within a custom tool](/oss/how-to/tool_configure/)

</Info>

If you have [tools](/oss/concepts/tools/) that call [chat models](/oss/concepts/chat_models/), [retrievers](/oss/concepts/retrievers/), or other [runnables](/oss/concepts/runnables/), you may want to access [internal events](https://python.langchain.com/docs/how_to/streaming/#event-reference) from those runnables or configure them with additional properties. This guide shows you how to manually pass parameters properly so that you can do this using the `astream_events()` method.

<Warning>
**Compatibility**


LangChain cannot automatically propagate configuration, including callbacks necessary for `astream_events()`, to child runnables if you are running `async` code in `python<=3.10`. This is a common reason why you may fail to see events being emitted from custom runnables or tools.

If you are running `python<=3.10`, you will need to manually propagate the `RunnableConfig` object to the child runnable in async environments. For an example of how to manually propagate the config, see the implementation of the `bar` RunnableLambda below.

If you are running `python>=3.11`, the `RunnableConfig` will automatically propagate to child runnables in async environment. However, it is still a good idea to propagate the `RunnableConfig` manually if your code may run in older Python versions.

This guide also requires `langchain-core>=0.2.16`.
</Warning>

Say you have a custom tool that calls a chain that condenses its input by prompting a chat model to return only 10 words, then reversing the output. First, define it in a naive way:

<ChatModelTabs customVarName="model" />



```python
# | output: false
# | echo: false

import os
from getpass import getpass

from langchain_anthropic import ChatAnthropic

if "ANTHROPIC_API_KEY" not in os.environ:
    os.environ["ANTHROPIC_API_KEY"] = getpass()

model = ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0)
```


```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool


@tool
async def special_summarization_tool(long_text: str) -> str:
    """A tool that summarizes input text using advanced techniques."""
    prompt = ChatPromptTemplate.from_template(
        "You are an expert writer. Summarize the following text in 10 words or less:\n\n{long_text}"
    )

    def reverse(x: str):
        return x[::-1]

    chain = prompt | model | StrOutputParser() | reverse
    summary = await chain.ainvoke({"long_text": long_text})
    return summary
```

Invoking the tool directly works just fine:


```python
LONG_TEXT = """
NARRATOR:
(Black screen with text; The sound of buzzing bees can be heard)
According to all known laws of aviation, there is no way a bee should be able to fly. Its wings are too small to get its fat little body off the ground. The bee, of course, flies anyway because bees don't care what humans think is impossible.
BARRY BENSON:
(Barry is picking out a shirt)
Yellow, black. Yellow, black. Yellow, black. Yellow, black. Ooh, black and yellow! Let's shake it up a little.
JANET BENSON:
Barry! Breakfast is ready!
BARRY:
Coming! Hang on a second.
"""

await special_summarization_tool.ainvoke({"long_text": LONG_TEXT})
```



```output
'.yad noitaudarg rof tiftuo sesoohc yrraB ;scisyhp seifed eeB'
```


But if you wanted to access the raw output from the chat model rather than the full tool, you might try to use the [`astream_events()`](/oss/how-to/streaming/#using-stream-events) method and look for an `on_chat_model_end` event. Here's what happens:


```python
stream = special_summarization_tool.astream_events({"long_text": LONG_TEXT})

async for event in stream:
    if event["event"] == "on_chat_model_end":
        # Never triggers in python<=3.10!
        print(event)
```

You'll notice (unless you're running through this guide in `python>=3.11`) that there are no chat model events emitted from the child run!

This is because the example above does not pass the tool's config object into the internal chain. To fix this, redefine your tool to take a special parameter typed as `RunnableConfig` (see [this guide](/oss/how-to/tool_configure) for more details). You'll also need to pass that parameter through into the internal chain when executing it:


```python
from langchain_core.runnables import RunnableConfig


@tool
async def special_summarization_tool_with_config(
    long_text: str, config: RunnableConfig
) -> str:
    """A tool that summarizes input text using advanced techniques."""
    prompt = ChatPromptTemplate.from_template(
        "You are an expert writer. Summarize the following text in 10 words or less:\n\n{long_text}"
    )

    def reverse(x: str):
        return x[::-1]

    chain = prompt | model | StrOutputParser() | reverse
    # Pass the "config" object as an argument to any executed runnables
    summary = await chain.ainvoke({"long_text": long_text}, config=config)
    return summary
```

And now try the same `astream_events()` call as before with your new tool:


```python
stream = special_summarization_tool_with_config.astream_events({"long_text": LONG_TEXT})

async for event in stream:
    if event["event"] == "on_chat_model_end":
        print(event)
```
```output
{'event': 'on_chat_model_end', 'data': {'output': AIMessage(content='Bee defies physics; Barry chooses outfit for graduation day.', additional_kwargs={}, response_metadata={'stop_reason': 'end_turn', 'stop_sequence': None}, id='run-337ac14e-8da8-4c6d-a69f-1573f93b651e', usage_metadata={'input_tokens': 182, 'output_tokens': 19, 'total_tokens': 201, 'input_token_details': {'cache_creation': 0, 'cache_read': 0}}), 'input': {'messages': [[HumanMessage(content="You are an expert writer. Summarize the following text in 10 words or less:\n\n\nNARRATOR:\n(Black screen with text; The sound of buzzing bees can be heard)\nAccording to all known laws of aviation, there is no way a bee should be able to fly. Its wings are too small to get its fat little body off the ground. The bee, of course, flies anyway because bees don't care what humans think is impossible.\nBARRY BENSON:\n(Barry is picking out a shirt)\nYellow, black. Yellow, black. Yellow, black. Yellow, black. Ooh, black and yellow! Let's shake it up a little.\nJANET BENSON:\nBarry! Breakfast is ready!\nBARRY:\nComing! Hang on a second.\n", additional_kwargs={}, response_metadata={})]]}}, 'run_id': '337ac14e-8da8-4c6d-a69f-1573f93b651e', 'name': 'ChatAnthropic', 'tags': ['seq:step:2'], 'metadata': {'ls_provider': 'anthropic', 'ls_model_name': 'claude-3-5-sonnet-20240620', 'ls_model_type': 'chat', 'ls_temperature': 0.0, 'ls_max_tokens': 1024}, 'parent_ids': ['225beaa6-af73-4c91-b2d3-1afbbb88d53e']}
```
Awesome! This time there's an event emitted.

For streaming, `astream_events()` automatically calls internal runnables in a chain with streaming enabled if possible, so if you wanted to a stream of tokens as they are generated from the chat model, you could simply filter to look for `on_chat_model_stream` events with no other changes:


```python
stream = special_summarization_tool_with_config.astream_events({"long_text": LONG_TEXT})

async for event in stream:
    if event["event"] == "on_chat_model_stream":
        print(event)
```
```output
{'event': 'on_chat_model_stream', 'data': {'chunk': AIMessageChunk(content='', additional_kwargs={}, response_metadata={}, id='run-f5e049f7-4e98-4236-87ab-8cd1ce85a2d5', usage_metadata={'input_tokens': 182, 'output_tokens': 2, 'total_tokens': 184, 'input_token_details': {'cache_creation': 0, 'cache_read': 0}})}, 'run_id': 'f5e049f7-4e98-4236-87ab-8cd1ce85a2d5', 'name': 'ChatAnthropic', 'tags': ['seq:step:2'], 'metadata': {'ls_provider': 'anthropic', 'ls_model_name': 'claude-3-5-sonnet-20240620', 'ls_model_type': 'chat', 'ls_temperature': 0.0, 'ls_max_tokens': 1024}, 'parent_ids': ['51858043-b301-4b76-8abb-56218e405283']}
{'event': 'on_chat_model_stream', 'data': {'chunk': AIMessageChunk(content='Bee', additional_kwargs={}, response_metadata={}, id='run-f5e049f7-4e98-4236-87ab-8cd1ce85a2d5')}, 'run_id': 'f5e049f7-4e98-4236-87ab-8cd1ce85a2d5', 'name': 'ChatAnthropic', 'tags': ['seq:step:2'], 'metadata': {'ls_provider': 'anthropic', 'ls_model_name': 'claude-3-5-sonnet-20240620', 'ls_model_type': 'chat', 'ls_temperature': 0.0, 'ls_max_tokens': 1024}, 'parent_ids': ['51858043-b301-4b76-8abb-56218e405283']}
{'event': 'on_chat_model_stream', 'data': {'chunk': AIMessageChunk(content=' defies physics;', additional_kwargs={}, response_metadata={}, id='run-f5e049f7-4e98-4236-87ab-8cd1ce85a2d5')}, 'run_id': 'f5e049f7-4e98-4236-87ab-8cd1ce85a2d5', 'name': 'ChatAnthropic', 'tags': ['seq:step:2'], 'metadata': {'ls_provider': 'anthropic', 'ls_model_name': 'claude-3-5-sonnet-20240620', 'ls_model_type': 'chat', 'ls_temperature': 0.0, 'ls_max_tokens': 1024}, 'parent_ids': ['51858043-b301-4b76-8abb-56218e405283']}
{'event': 'on_chat_model_stream', 'data': {'chunk': AIMessageChunk(content=' Barry chooses outfit for', additional_kwargs={}, response_metadata={}, id='run-f5e049f7-4e98-4236-87ab-8cd1ce85a2d5')}, 'run_id': 'f5e049f7-4e98-4236-87ab-8cd1ce85a2d5', 'name': 'ChatAnthropic', 'tags': ['seq:step:2'], 'metadata': {'ls_provider': 'anthropic', 'ls_model_name': 'claude-3-5-sonnet-20240620', 'ls_model_type': 'chat', 'ls_temperature': 0.0, 'ls_max_tokens': 1024}, 'parent_ids': ['51858043-b301-4b76-8abb-56218e405283']}
{'event': 'on_chat_model_stream', 'data': {'chunk': AIMessageChunk(content=' graduation day.', additional_kwargs={}, response_metadata={}, id='run-f5e049f7-4e98-4236-87ab-8cd1ce85a2d5')}, 'run_id': 'f5e049f7-4e98-4236-87ab-8cd1ce85a2d5', 'name': 'ChatAnthropic', 'tags': ['seq:step:2'], 'metadata': {'ls_provider': 'anthropic', 'ls_model_name': 'claude-3-5-sonnet-20240620', 'ls_model_type': 'chat', 'ls_temperature': 0.0, 'ls_max_tokens': 1024}, 'parent_ids': ['51858043-b301-4b76-8abb-56218e405283']}
{'event': 'on_chat_model_stream', 'data': {'chunk': AIMessageChunk(content='', additional_kwargs={}, response_metadata={'stop_reason': 'end_turn', 'stop_sequence': None}, id='run-f5e049f7-4e98-4236-87ab-8cd1ce85a2d5', usage_metadata={'input_tokens': 0, 'output_tokens': 17, 'total_tokens': 17, 'input_token_details': {}})}, 'run_id': 'f5e049f7-4e98-4236-87ab-8cd1ce85a2d5', 'name': 'ChatAnthropic', 'tags': ['seq:step:2'], 'metadata': {'ls_provider': 'anthropic', 'ls_model_name': 'claude-3-5-sonnet-20240620', 'ls_model_type': 'chat', 'ls_temperature': 0.0, 'ls_max_tokens': 1024}, 'parent_ids': ['51858043-b301-4b76-8abb-56218e405283']}
```
## Next steps

You've now seen how to stream events from within a tool. Next, check out the following guides for more on using tools:

- Pass [runtime values to tools](/oss/how-to/tool_runtime)
- Pass [tool results back to a model](/oss/how-to/tool_results_pass_to_model)
- [Dispatch custom callback events](/oss/how-to/callbacks_custom_events)

You can also check out some more specific uses of tool calling:

- Building [tool-using chains and agents](/docs/how_to#tools)
- Getting [structured outputs](/oss/how-to/structured_output/) from models
