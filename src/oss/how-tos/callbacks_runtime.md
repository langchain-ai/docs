# How to pass callbacks in at runtime

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:

- [Callbacks](/oss/concepts/callbacks)
- [Custom callback handlers](/oss/how-to/custom_callbacks)

</Info>

In many cases, it is advantageous to pass in handlers instead when running the object. When we pass through [`CallbackHandlers`](https://python.langchain.com/api_reference/core/callbacks/langchain_core.callbacks.base.BaseCallbackHandler.html#langchain-core-callbacks-base-basecallbackhandler) using the `callbacks` keyword arg when executing a run, those callbacks will be issued by all nested objects involved in the execution. For example, when a handler is passed through to an Agent, it will be used for all callbacks related to the agent and all the objects involved in the agent's execution, in this case, the Tools and LLM.

This prevents us from having to manually attach the handlers to each individual nested object. Here's an example:


```python
# | output: false
# | echo: false

%pip install -qU langchain langchain_anthropic

import getpass
import os

os.environ["ANTHROPIC_API_KEY"] = getpass.getpass()
```


```python
from typing import Any, Dict, List

from langchain_anthropic import ChatAnthropic
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult
from langchain_core.prompts import ChatPromptTemplate


class LoggingHandler(BaseCallbackHandler):
    def on_chat_model_start(
        self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], **kwargs
    ) -> None:
        print("Chat model started")

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        print(f"Chat model ended, response: {response}")

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs
    ) -> None:
        print(f"Chain {serialized.get('name')} started")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        print(f"Chain ended, outputs: {outputs}")


callbacks = [LoggingHandler()]
llm = ChatAnthropic(model="claude-3-7-sonnet-20250219")
prompt = ChatPromptTemplate.from_template("What is 1 + {number}?")

chain = prompt | llm

chain.invoke({"number": "2"}, config={"callbacks": callbacks})
```
```output
Error in LoggingHandler.on_chain_start callback: AttributeError("'NoneType' object has no attribute 'get'")
``````output
Chain ChatPromptTemplate started
Chain ended, outputs: messages=[HumanMessage(content='What is 1 + 2?', additional_kwargs={}, response_metadata={})]
Chat model started
Chat model ended, response: generations=[[ChatGeneration(text='1 + 2 = 3', message=AIMessage(content='1 + 2 = 3', additional_kwargs={}, response_metadata={'id': 'msg_019ieJt8K32iC77qBbQmSa9m', 'model': 'claude-3-7-sonnet-20250219', 'stop_reason': 'end_turn', 'stop_sequence': None, 'usage': {'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'input_tokens': 16, 'output_tokens': 13, 'server_tool_use': None, 'service_tier': 'standard'}, 'model_name': 'claude-3-7-sonnet-20250219'}, id='run--2f596356-99c9-45ef-94ff-fb170072abdf-0', usage_metadata={'input_tokens': 16, 'output_tokens': 13, 'total_tokens': 29, 'input_token_details': {'cache_read': 0, 'cache_creation': 0}}))]] llm_output={'id': 'msg_019ieJt8K32iC77qBbQmSa9m', 'model': 'claude-3-7-sonnet-20250219', 'stop_reason': 'end_turn', 'stop_sequence': None, 'usage': {'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'input_tokens': 16, 'output_tokens': 13, 'server_tool_use': None, 'service_tier': 'standard'}, 'model_name': 'claude-3-7-sonnet-20250219'} run=None type='LLMResult'
Chain ended, outputs: content='1 + 2 = 3' additional_kwargs={} response_metadata={'id': 'msg_019ieJt8K32iC77qBbQmSa9m', 'model': 'claude-3-7-sonnet-20250219', 'stop_reason': 'end_turn', 'stop_sequence': None, 'usage': {'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'input_tokens': 16, 'output_tokens': 13, 'server_tool_use': None, 'service_tier': 'standard'}, 'model_name': 'claude-3-7-sonnet-20250219'} id='run--2f596356-99c9-45ef-94ff-fb170072abdf-0' usage_metadata={'input_tokens': 16, 'output_tokens': 13, 'total_tokens': 29, 'input_token_details': {'cache_read': 0, 'cache_creation': 0}}
```


```output
AIMessage(content='1 + 2 = 3', additional_kwargs={}, response_metadata={'id': 'msg_019ieJt8K32iC77qBbQmSa9m', 'model': 'claude-3-7-sonnet-20250219', 'stop_reason': 'end_turn', 'stop_sequence': None, 'usage': {'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'input_tokens': 16, 'output_tokens': 13, 'server_tool_use': None, 'service_tier': 'standard'}, 'model_name': 'claude-3-7-sonnet-20250219'}, id='run--2f596356-99c9-45ef-94ff-fb170072abdf-0', usage_metadata={'input_tokens': 16, 'output_tokens': 13, 'total_tokens': 29, 'input_token_details': {'cache_read': 0, 'cache_creation': 0}})
```


If there are already existing callbacks associated with a module, these will run in addition to any passed in at runtime.

## Next steps

You've now learned how to pass callbacks at runtime.

Next, check out the other how-to guides in this section, such as how to [pass callbacks into a module constructor](/oss/how-to/custom_callbacks).
