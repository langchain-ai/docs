---
sidebar_label: AWS Bedrock
---

# ChatBedrock

This doc will help you get started with AWS Bedrock [chat models](/oss/concepts/chat_models). Amazon Bedrock is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies like AI21 Labs, Anthropic, Cohere, Meta, Stability AI, and Amazon via a single API, along with a broad set of capabilities you need to build generative AI applications with security, privacy, and responsible AI. Using Amazon Bedrock, you can easily experiment with and evaluate top FMs for your use case, privately customize them with your data using techniques such as fine-tuning and Retrieval Augmented Generation (RAG), and build agents that execute tasks using your enterprise systems and data sources. Since Amazon Bedrock is serverless, you don't have to manage any infrastructure, and you can securely integrate and deploy generative AI capabilities into your applications using the AWS services you are already familiar with.

AWS Bedrock maintains a [Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) which provides a unified conversational interface for Bedrock models. This API does not yet support custom models. You can see a list of all [models that are supported here](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html).

<Info>
**We recommend the Converse API for users who do not need to use custom models. It can be accessed using [ChatBedrockConverse](https://python.langchain.com/api_reference/aws/chat_models/langchain_aws.chat_models.bedrock_converse.ChatBedrockConverse.html).**


</Info>

For detailed documentation of all Bedrock features and configurations head to the [API reference](https://python.langchain.com/api_reference/aws/chat_models/langchain_aws.chat_models.bedrock_converse.ChatBedrockConverse.html).

## Overview
### Integration details

| Class | Package | Local | Serializable | [JS support](https://js.langchain.com/docs/integrations/chat/bedrock) | Package downloads | Package latest |
| :--- | :--- | :---: | :---: |  :---: | :---: | :---: |
| [ChatBedrock](https://python.langchain.com/api_reference/aws/chat_models/langchain_aws.chat_models.bedrock.ChatBedrock.html) | [langchain-aws](https://python.langchain.com/api_reference/aws/index.html) | ❌ | beta | ✅ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-aws?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-aws?style=flat-square&label=%20) |
| [ChatBedrockConverse](https://python.langchain.com/api_reference/aws/chat_models/langchain_aws.chat_models.bedrock_converse.ChatBedrockConverse.html) | [langchain-aws](https://python.langchain.com/api_reference/aws/index.html) | ❌ | beta | ✅ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-aws?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-aws?style=flat-square&label=%20) |

### Model features

The below apply to both `ChatBedrock` and `ChatBedrockConverse`.

| [Tool calling](/oss/how-to/tool_calling) | [Structured output](/oss/how-to/structured_output/) | JSON mode | [Image input](/oss/how-to/multimodal_inputs/) | Audio input | Video input | [Token-level streaming](/oss/how-to/chat_streaming/) | Native async | [Token usage](/oss/how-to/chat_token_usage_tracking/) | [Logprobs](/oss/how-to/logprobs/) |
| :---: | :---: | :---: | :---: |  :---: | :---: | :---: | :---: | :---: | :---: |
| ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ |

## Setup

To access Bedrock models you'll need to create an AWS account, set up the Bedrock API service, get an access key ID and secret key, and install the `langchain-aws` integration package.

### Credentials

Head to the [AWS docs](https://docs.aws.amazon.com/bedrock/latest/userguide/setting-up.html) to sign up to AWS and setup your credentials.

Alternatively, `ChatBedrockConverse` will read from the following environment variables by default:


```python
# os.environ["AWS_ACCESS_KEY_ID"] = "..."
# os.environ["AWS_SECRET_ACCESS_KEY"] = "..."

# Not required unless using temporary credentials.
# os.environ["AWS_SESSION_TOKEN"] = "..."
```

You'll also need to turn on model access for your account, which you can do by following [these instructions](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html).

To enable automated tracing of your model calls, set your [LangSmith](https://docs.smith.langchain.com/) API key:


```python
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"
```

### Installation

The LangChain Bedrock integration lives in the `langchain-aws` package:


```python
%pip install -qU langchain-aws
```

## Instantiation

Now we can instantiate our model object and generate chat completions:


```python
from langchain_aws import ChatBedrockConverse

llm = ChatBedrockConverse(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    # region_name=...,
    # aws_access_key_id=...,
    # aws_secret_access_key=...,
    # aws_session_token=...,
    # temperature=...,
    # max_tokens=...,
    # other params...
)
```

## Invocation


```python
messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]
ai_msg = llm.invoke(messages)
ai_msg
```



```output
AIMessage(content="J'adore la programmation.", additional_kwargs={}, response_metadata={'ResponseMetadata': {'RequestId': 'b07d1630-06f2-44b1-82bf-e82538dd2215', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Wed, 16 Apr 2025 19:35:34 GMT', 'content-type': 'application/json', 'content-length': '206', 'connection': 'keep-alive', 'x-amzn-requestid': 'b07d1630-06f2-44b1-82bf-e82538dd2215'}, 'RetryAttempts': 0}, 'stopReason': 'end_turn', 'metrics': {'latencyMs': [488]}, 'model_name': 'anthropic.claude-3-5-sonnet-20240620-v1:0'}, id='run-d09ed928-146a-4336-b1fd-b63c9e623494-0', usage_metadata={'input_tokens': 29, 'output_tokens': 11, 'total_tokens': 40, 'input_token_details': {'cache_creation': 0, 'cache_read': 0}})
```



```python
print(ai_msg.content)
```
```output
J'adore la programmation.
```
### Streaming

Note that `ChatBedrockConverse` emits content blocks while streaming:


```python
for chunk in llm.stream(messages):
    print(chunk)
```
```output
content=[] additional_kwargs={} response_metadata={} id='run-d0e0836e-7146-4c3d-97c7-ad23dac6febd'
content=[{'type': 'text', 'text': 'J', 'index': 0}] additional_kwargs={} response_metadata={} id='run-d0e0836e-7146-4c3d-97c7-ad23dac6febd'
content=[{'type': 'text', 'text': "'adore la", 'index': 0}] additional_kwargs={} response_metadata={} id='run-d0e0836e-7146-4c3d-97c7-ad23dac6febd'
content=[{'type': 'text', 'text': ' programmation.', 'index': 0}] additional_kwargs={} response_metadata={} id='run-d0e0836e-7146-4c3d-97c7-ad23dac6febd'
content=[{'index': 0}] additional_kwargs={} response_metadata={} id='run-d0e0836e-7146-4c3d-97c7-ad23dac6febd'
content=[] additional_kwargs={} response_metadata={'stopReason': 'end_turn'} id='run-d0e0836e-7146-4c3d-97c7-ad23dac6febd'
content=[] additional_kwargs={} response_metadata={'metrics': {'latencyMs': 600}, 'model_name': 'anthropic.claude-3-5-sonnet-20240620-v1:0'} id='run-d0e0836e-7146-4c3d-97c7-ad23dac6febd' usage_metadata={'input_tokens': 29, 'output_tokens': 11, 'total_tokens': 40, 'input_token_details': {'cache_creation': 0, 'cache_read': 0}}
```
You can filter to text using the [.text()](https://python.langchain.com/api_reference/core/messages/langchain_core.messages.ai.AIMessage.html#langchain_core.messages.ai.AIMessage.text) method on the output:


```python
for chunk in llm.stream(messages):
    print(chunk.text(), end="|")
```
```output
|J|'adore la| programmation.||||
```
## Extended Thinking 

This guide focuses on implementing Extended Thinking using AWS Bedrock with LangChain's `ChatBedrockConverse` integration.

### Supported Models

Extended Thinking is available for the following Claude models on AWS Bedrock:

| Model | Model ID |
|-------|----------|
| **Claude Opus 4** | `anthropic.claude-opus-4-20250514-v1:0` |
| **Claude Sonnet 4** | `anthropic.claude-sonnet-4-20250514-v1:0` |
| **Claude 3.7 Sonnet** | `us.anthropic.claude-3-7-sonnet-20250219-v1:0` |



```python
from langchain_aws import ChatBedrockConverse

llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    region_name="us-west-2",
    max_tokens=4096,
    additional_model_request_fields={
        "thinking": {"type": "enabled", "budget_tokens": 1024},
    },
)

ai_msg = llm.invoke(messages)
ai_msg
```



```output
AIMessage(content=[{'type': 'reasoning_content', 'reasoning_content': {'text': 'The user wants me to translate "I love programming" from English to French.\n\n"I love" translates to "J\'aime" or "J\'adore" in French\n"Programming" translates to "la programmation" in French\n\nSo the translation would be "J\'aime la programmation" or "J\'adore la programmation"\n\nBoth are correct, but "J\'aime" is more commonly used for expressing love/liking something.', 'signature': 'EpgECkgIBRABGAIqQDub6nRpiusjbxZONXVlGXg5ZjUY1Eka1Yp4oBBHmRqGjId+StTBPuwD3CXLyb2rUDRhSc3hTpTM4krVqlFZrIsSDI/WLa1mu38DDqt1HRoMUjm+jF+03MZFD+WQIjBZtHaYiqgY0JQgU0NdXDwwBSZX44gXwuX9EDekh12VM1ysq+WxVtkp0WMU0dKCJo4q/QKpguFFlZtEZjF9PftzOgTIyy+1H5pY+Dsb2pnrGtfAgwTR7PuZ/d8ibY0A8ywjVEZtGm+PtcnCJiK53BWxhGYOtxnfN/RRKtuZhvPQj+QQOWeRWqH+GcbeISCgyTYn5WG75fmVL707byjQZ3IuhMfyZWmiTFE2fc4Jn/bxX7OsU+DbTWv2K1a+g7eW+dvQwYzCBO1hfEn4699/CHII8UAcHh1L3bnxOWGKkeVQ0KMfgfwVb0vuGG4QBYKIDs87QL414i69D68DxqCTZAHK4lMA6Xs7zW+m0MMCct4iHRnJI8kat1mlBEpMz6NRo9KacZJXpLJxofIU4ho7R5/QHccdni0IidNkUtrLBSB3toNJoQEcStts2UR67NHTxn47zk1/hi4v4Ahtw9OEQFONaH6XaG1wjpqEdjQ8/Tmg9eB6ZLoQ4sQfhcMF8Uo3hHbBY8jA3jZ+9pa9VbuVbO6Eup8NX3XXZm2nk50OMWX7hBwgBmlZbEew6pWFu7+13EkYAQ=='}}, {'type': 'text', 'text': "J'aime la programmation."}], additional_kwargs={}, response_metadata={'ResponseMetadata': {'RequestId': '169ca92f-19c9-480c-9fc3-4e5284507e67', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Tue, 22 Jul 2025 04:40:22 GMT', 'content-type': 'application/json', 'content-length': '1498', 'connection': 'keep-alive', 'x-amzn-requestid': '169ca92f-19c9-480c-9fc3-4e5284507e67'}, 'RetryAttempts': 0}, 'stopReason': 'end_turn', 'metrics': {'latencyMs': [2839]}, 'model_name': 'us.anthropic.claude-sonnet-4-20250514-v1:0'}, id='run--42e05e5d-ba86-4dce-9e29-2a4ba32c5804-0', usage_metadata={'input_tokens': 58, 'output_tokens': 122, 'total_tokens': 180, 'input_token_details': {'cache_creation': 0, 'cache_read': 0}})
```



```python
print(ai_msg.content)
```
```output
[{'type': 'reasoning_content', 'reasoning_content': {'text': 'The user wants me to translate "I love programming" from English to French.\n\n"I love" translates to "J\'aime" or "J\'adore" in French\n"Programming" translates to "la programmation" in French\n\nSo the translation would be "J\'aime la programmation" or "J\'adore la programmation"\n\nBoth are correct, but "J\'aime" is more commonly used for expressing love/liking something.', 'signature': 'EpgECkgIBRABGAIqQDub6nRpiusjbxZONXVlGXg5ZjUY1Eka1Yp4oBBHmRqGjId+StTBPuwD3CXLyb2rUDRhSc3hTpTM4krVqlFZrIsSDI/WLa1mu38DDqt1HRoMUjm+jF+03MZFD+WQIjBZtHaYiqgY0JQgU0NdXDwwBSZX44gXwuX9EDekh12VM1ysq+WxVtkp0WMU0dKCJo4q/QKpguFFlZtEZjF9PftzOgTIyy+1H5pY+Dsb2pnrGtfAgwTR7PuZ/d8ibY0A8ywjVEZtGm+PtcnCJiK53BWxhGYOtxnfN/RRKtuZhvPQj+QQOWeRWqH+GcbeISCgyTYn5WG75fmVL707byjQZ3IuhMfyZWmiTFE2fc4Jn/bxX7OsU+DbTWv2K1a+g7eW+dvQwYzCBO1hfEn4699/CHII8UAcHh1L3bnxOWGKkeVQ0KMfgfwVb0vuGG4QBYKIDs87QL414i69D68DxqCTZAHK4lMA6Xs7zW+m0MMCct4iHRnJI8kat1mlBEpMz6NRo9KacZJXpLJxofIU4ho7R5/QHccdni0IidNkUtrLBSB3toNJoQEcStts2UR67NHTxn47zk1/hi4v4Ahtw9OEQFONaH6XaG1wjpqEdjQ8/Tmg9eB6ZLoQ4sQfhcMF8Uo3hHbBY8jA3jZ+9pa9VbuVbO6Eup8NX3XXZm2nk50OMWX7hBwgBmlZbEew6pWFu7+13EkYAQ=='}}, {'type': 'text', 'text': "J'aime la programmation."}]
```
### How extended thinking works

When extended thinking is turned on, Claude creates thinking content blocks where it outputs its internal reasoning. Claude incorporates insights from this reasoning before crafting a final response. The API response will include thinking content blocks, followed by text content blocks.


```python
next_messages = messages + [("ai", ai_msg.content), ("human", "I love AI")]
next_messages
```



```output
[('system',
  'You are a helpful assistant that translates English to French. Translate the user sentence.'),
 ('human', 'I love programming.'),
 ('ai',
  [{'type': 'reasoning_content',
    'reasoning_content': {'text': 'The user wants me to translate "I love programming" from English to French.\n\n"I love" translates to "J\'aime" or "J\'adore" in French\n"Programming" translates to "la programmation" in French\n\nSo the translation would be "J\'aime la programmation" or "J\'adore la programmation"\n\nBoth are correct, but "J\'aime" is more commonly used for expressing love/liking something.',
     'signature': 'EpgECkgIBRABGAIqQDub6nRpiusjbxZONXVlGXg5ZjUY1Eka1Yp4oBBHmRqGjId+StTBPuwD3CXLyb2rUDRhSc3hTpTM4krVqlFZrIsSDI/WLa1mu38DDqt1HRoMUjm+jF+03MZFD+WQIjBZtHaYiqgY0JQgU0NdXDwwBSZX44gXwuX9EDekh12VM1ysq+WxVtkp0WMU0dKCJo4q/QKpguFFlZtEZjF9PftzOgTIyy+1H5pY+Dsb2pnrGtfAgwTR7PuZ/d8ibY0A8ywjVEZtGm+PtcnCJiK53BWxhGYOtxnfN/RRKtuZhvPQj+QQOWeRWqH+GcbeISCgyTYn5WG75fmVL707byjQZ3IuhMfyZWmiTFE2fc4Jn/bxX7OsU+DbTWv2K1a+g7eW+dvQwYzCBO1hfEn4699/CHII8UAcHh1L3bnxOWGKkeVQ0KMfgfwVb0vuGG4QBYKIDs87QL414i69D68DxqCTZAHK4lMA6Xs7zW+m0MMCct4iHRnJI8kat1mlBEpMz6NRo9KacZJXpLJxofIU4ho7R5/QHccdni0IidNkUtrLBSB3toNJoQEcStts2UR67NHTxn47zk1/hi4v4Ahtw9OEQFONaH6XaG1wjpqEdjQ8/Tmg9eB6ZLoQ4sQfhcMF8Uo3hHbBY8jA3jZ+9pa9VbuVbO6Eup8NX3XXZm2nk50OMWX7hBwgBmlZbEew6pWFu7+13EkYAQ=='}},
   {'type': 'text', 'text': "J'aime la programmation."}]),
 ('human', 'I love AI')]
```



```python
ai_msg = llm.invoke(next_messages)
ai_msg
```



```output
AIMessage(content=[{'type': 'reasoning_content', 'reasoning_content': {'text': 'The user wants me to translate "I love AI" from English to French. \n\n"I love" translates to "J\'aime" in French.\n"AI" stands for "Artificial Intelligence" which in French is "Intelligence Artificielle" or abbreviated as "IA".\n\nSo the translation would be "J\'aime l\'IA" (using the abbreviation) or "J\'aime l\'intelligence artificielle" (using the full term).\n\nI think using the abbreviation "IA" would be more natural and commonly used, similar to how we use "AI" in English.', 'signature': 'EoMFCkgIBRABGAIqQOwp9d0YWm8NctfL9lf1MeWR1OxeAKB3Es19Lei2bdHQ4W0ezTK4wVcm/VLM+7kICX2aB9RAmUD5sJxoKHfdX38SDIR/aSJhHZifGOHqwBoMhzNsyPmB7FFNvNESIjBMVRpRUDTFGn5+nL0x5CjWhKA8H/XFnKYRrUyMYb1n7lCQA7BeEjsaWwxZ3YV9rZsq6APuaXaA40Bt+KnpPOo06r72L/DceliRAw1a6cuT5E0Dv0eIAOYblbXaKYn0jy8UzTUuctOP3As/zT5pK5yC+Rx0d2l9kuP3+COERM98u0R04bWn6qh0HcyE+zNc7c4YWkncjdmOxF/j6OxhcMhZEoX2035v9eUJ9+O/u1xaff08YAEfg7TGWrSIwalpjs1mzWA9ijKg8YyjmXjWnMeFn0z6LDqLaaKc+nC8IN9SLwA/eHpf/ayoEgmogn7gWzijW8MDbnlwpQDS75wK7An3RMEcpWD/OXrKb1EhWKEmOBro5BOTGsfK3ZDveRL0aCBINdOu+AHMQDFXJ04cRDEjs9GE3YC218UcFtS42TFO7/Ct5CYCTknETPx93zcGTOM2VPOZ02Uem1A7Nda/Fa4l2b03EUEtwlgske5K1RbeohN9sclxYsxX5nGJ5sSZurVCk9plkyTG3aiPvbohfVVarVgukKoKwoMDYz5rHVscWlUe+qeqJE/H+KKlhtzO+lWWDN4knqeYsZ55flO5Hq4vT20QCYnF8hcUx07ngGKXuGID9n5kFnLsP8sBUHYKm7bmopFFZvfPcmsqiV9yvG/8Ly9DHbmY5ZwxyrbdJCFT6HD6kq/mEBDftZ6dhmyKMimJBfbTj7d3VAILbRgB'}}, {'type': 'text', 'text': "J'aime l'IA."}], additional_kwargs={}, response_metadata={'ResponseMetadata': {'RequestId': '023799d6-7ed5-4e49-8ad7-7460a49a9a45', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Tue, 22 Jul 2025 04:40:34 GMT', 'content-type': 'application/json', 'content-length': '1737', 'connection': 'keep-alive', 'x-amzn-requestid': '023799d6-7ed5-4e49-8ad7-7460a49a9a45'}, 'RetryAttempts': 0}, 'stopReason': 'end_turn', 'metrics': {'latencyMs': [3473]}, 'model_name': 'us.anthropic.claude-sonnet-4-20250514-v1:0'}, id='run--ca8abc92-60a9-4bd1-93b4-7788496eda7a-0', usage_metadata={'input_tokens': 75, 'output_tokens': 153, 'total_tokens': 228, 'input_token_details': {'cache_creation': 0, 'cache_read': 0}})
```



```python
print(ai_msg.content)
```
```output
[{'type': 'reasoning_content', 'reasoning_content': {'text': 'The user wants me to translate "I love AI" from English to French. \n\n"I love" translates to "J\'aime" in French.\n"AI" stands for "Artificial Intelligence" which in French is "Intelligence Artificielle" or abbreviated as "IA".\n\nSo the translation would be "J\'aime l\'IA" (using the abbreviation) or "J\'aime l\'intelligence artificielle" (using the full term).\n\nI think using the abbreviation "IA" would be more natural and commonly used, similar to how we use "AI" in English.', 'signature': 'EoMFCkgIBRABGAIqQOwp9d0YWm8NctfL9lf1MeWR1OxeAKB3Es19Lei2bdHQ4W0ezTK4wVcm/VLM+7kICX2aB9RAmUD5sJxoKHfdX38SDIR/aSJhHZifGOHqwBoMhzNsyPmB7FFNvNESIjBMVRpRUDTFGn5+nL0x5CjWhKA8H/XFnKYRrUyMYb1n7lCQA7BeEjsaWwxZ3YV9rZsq6APuaXaA40Bt+KnpPOo06r72L/DceliRAw1a6cuT5E0Dv0eIAOYblbXaKYn0jy8UzTUuctOP3As/zT5pK5yC+Rx0d2l9kuP3+COERM98u0R04bWn6qh0HcyE+zNc7c4YWkncjdmOxF/j6OxhcMhZEoX2035v9eUJ9+O/u1xaff08YAEfg7TGWrSIwalpjs1mzWA9ijKg8YyjmXjWnMeFn0z6LDqLaaKc+nC8IN9SLwA/eHpf/ayoEgmogn7gWzijW8MDbnlwpQDS75wK7An3RMEcpWD/OXrKb1EhWKEmOBro5BOTGsfK3ZDveRL0aCBINdOu+AHMQDFXJ04cRDEjs9GE3YC218UcFtS42TFO7/Ct5CYCTknETPx93zcGTOM2VPOZ02Uem1A7Nda/Fa4l2b03EUEtwlgske5K1RbeohN9sclxYsxX5nGJ5sSZurVCk9plkyTG3aiPvbohfVVarVgukKoKwoMDYz5rHVscWlUe+qeqJE/H+KKlhtzO+lWWDN4knqeYsZ55flO5Hq4vT20QCYnF8hcUx07ngGKXuGID9n5kFnLsP8sBUHYKm7bmopFFZvfPcmsqiV9yvG/8Ly9DHbmY5ZwxyrbdJCFT6HD6kq/mEBDftZ6dhmyKMimJBfbTj7d3VAILbRgB'}}, {'type': 'text', 'text': "J'aime l'IA."}]
```
## Prompt caching

Bedrock supports [caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) of elements of your prompts, including messages and tools. This allows you to re-use large documents, instructions, [few-shot documents](/oss/concepts/few_shot_prompting/), and other data to reduce latency and costs.

<Note>
**Not all models support prompt caching. See supported models [here](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html#prompt-caching-models).**


</Note>

To enable caching on an element of a prompt, mark its associated content block using the `cachePoint` key. See example below:


```python
import requests
from langchain_aws import ChatBedrockConverse

llm = ChatBedrockConverse(model="us.anthropic.claude-3-7-sonnet-20250219-v1:0")

# Pull LangChain readme
get_response = requests.get(
    "https://raw.githubusercontent.com/langchain-ai/langchain/master/README.md"
)
readme = get_response.text

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "What's LangChain, according to its README?",
            },
            {
                "type": "text",
                "text": f"{readme}",
            },
            {
                "cachePoint": {"type": "default"},
            },
        ],
    },
]

response_1 = llm.invoke(messages)
response_2 = llm.invoke(messages)

usage_1 = response_1.usage_metadata["input_token_details"]
usage_2 = response_2.usage_metadata["input_token_details"]

print(f"First invocation:\n{usage_1}")
print(f"\nSecond:\n{usage_2}")
```
```output
First invocation:
{'cache_creation': 1528, 'cache_read': 0}

Second:
{'cache_creation': 0, 'cache_read': 1528}
```
## Chaining

We can [chain](/oss/how-to/sequence/) our model with a prompt template like so:


```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that translates {input_language} to {output_language}.",
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm
chain.invoke(
    {
        "input_language": "English",
        "output_language": "German",
        "input": "I love programming.",
    }
)
```



```output
AIMessage(content="Here's the German translation:\n\nIch liebe das Programmieren.", additional_kwargs={}, response_metadata={'ResponseMetadata': {'RequestId': '1de3d7c0-8062-4f7e-bb8a-8f725b97a8b0', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Wed, 16 Apr 2025 19:32:51 GMT', 'content-type': 'application/json', 'content-length': '243', 'connection': 'keep-alive', 'x-amzn-requestid': '1de3d7c0-8062-4f7e-bb8a-8f725b97a8b0'}, 'RetryAttempts': 0}, 'stopReason': 'end_turn', 'metrics': {'latencyMs': [719]}, 'model_name': 'anthropic.claude-3-5-sonnet-20240620-v1:0'}, id='run-7021fcd7-704e-496b-a92e-210139614402-0', usage_metadata={'input_tokens': 23, 'output_tokens': 19, 'total_tokens': 42, 'input_token_details': {'cache_creation': 0, 'cache_read': 0}})
```


## API reference

For detailed documentation of all ChatBedrock features and configurations head to the API reference: https://python.langchain.com/api_reference/aws/chat_models/langchain_aws.chat_models.bedrock.ChatBedrock.html

For detailed documentation of all ChatBedrockConverse features and configurations head to the API reference: https://python.langchain.com/api_reference/aws/chat_models/langchain_aws.chat_models.bedrock_converse.ChatBedrockConverse.html
