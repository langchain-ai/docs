---
title: ChatQwQ
---

This will help you get started with QwQ [chat models](../../concepts/chat_models). For detailed documentation of all ChatQwQ features and configurations head to the [API reference](https://pypi.org/project/langchain-qwq/).

## Overview

### Integration details

| Class | Package | Local | Serializable | Downloads | Version |
| :--- | :--- | :---: |  :---: | :---: | :---: |
| [ChatQwQ](https://pypi.org/project/langchain-qwq/) | [langchain-qwq](https://pypi.org/project/langchain-qwq/) | ❌ | beta | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-qwq?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-qwq?style=flat-square&label=%20) |

### Model features

| [Tool calling](../../how_to/tool_calling.ipynb) | [Structured output](../../how_to/structured_output.ipynb) | JSON mode | [Image input](../../how_to/multimodal_inputs.ipynb) | Audio input | Video input | [Token-level streaming](../../how_to/chat_streaming.ipynb) | Native async | [Token usage](../../how_to/chat_token_usage_tracking.ipynb) | [Logprobs](../../how_to/logprobs.ipynb) |
| :---: | :---: | :---: | :---: |  :---: | :---: | :---: | :---: | :---: | :---: |
| ✅ | ✅ | ✅ |❌  | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |

## Setup

To access QwQ models you'll need to create an Alibaba Cloud account, get an API key, and install the `langchain-qwq` integration package.

### Credentials

Head to [Alibaba's API Key page](https://account.alibabacloud.com/login/login.htm?oauth_callback=https%3A%2F%2Fbailian.console.alibabacloud.com%2F%3FapiKey%3D1&lang=en#/api-key) to sign up to Alibaba Cloud and generate an API key. Once you've done this set the `DASHSCOPE_API_KEY` environment variable:

```python
import getpass
import os

if not os.getenv("DASHSCOPE_API_KEY"):
    os.environ["DASHSCOPE_API_KEY"] = getpass.getpass("Enter your Dashscope API key: ")
```

### Installation

The LangChain QwQ integration lives in the `langchain-qwq` package:

```python
%pip install -qU langchain-qwq
```

## Instantiation

Now we can instantiate our model object and generate chat completions:

```python
from langchain_qwq import ChatQwQ

llm = ChatQwQ(
    model="qwq-plus",
    max_tokens=3_000,
    timeout=None,
    max_retries=2,
    # other params...
)
```

## Invocation

```python
messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French."
        "Translate the user sentence.",
    ),
    ("human", "I love programming."),
]
ai_msg = llm.invoke(messages)
ai_msg
```

```output
AIMessage(content="J'aime la programmation.", additional_kwargs={'reasoning_content': 'Okay, the user wants me to translate "I love programming." into French. Let\'s start by breaking down the sentence. The subject is "I", which in French is "Je". The verb is "love", which in this context is present tense, so "aime". The object is "programming". Now, "programming" in French can be "la programmation". \n\nWait, should it be "programmation" or "programmation"? Let me confirm the spelling. Yes, "programmation" is correct. Now, putting it all together: "Je aime la programmation." Hmm, but in French, there\'s a tendency to contract "je" and "aime". Wait, actually, "je" followed by a vowel sound usually takes "j\'". So it should be "J\'aime la programmation." \n\nLet me double-check. "J\'aime" is the correct contraction for "I love". The definite article "la" is needed because "programmation" is a feminine noun. Yes, "programmation" is a feminine noun, so "la" is correct. \n\nIs there any other way to say it? Maybe "J\'adore la programmation" for "I love" in a stronger sense, but the user didn\'t specify the intensity. Since the original is straightforward, "J\'aime la programmation." is the direct translation. \n\nI think that\'s it. No mistakes there. So the final translation should be "J\'aime la programmation."'}, response_metadata={'model_name': 'qwq-plus'}, id='run-5045cd6a-edbd-4b2f-bf24-b7bdf3777fb9-0', usage_metadata={'input_tokens': 32, 'output_tokens': 326, 'total_tokens': 358, 'input_token_details': {}, 'output_token_details': {}})
```

## Chaining

We can [chain](../../how_to/sequence.ipynb) our model with a prompt template like so:

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate(
    [
        (
            "system",
            "You are a helpful assistant that translates"
            "{input_language} to {output_language}.",
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
AIMessage(content='Ich liebe das Programmieren.', additional_kwargs={'reasoning_content': 'Okay, the user wants me to translate "I love programming." into German. Let me think. The verb "love" is "lieben" or "mögen" in German, but "lieben" is more like love, while "mögen" is prefer. Since it\'s about programming, which is a strong affection, "lieben" is better. The subject is "I", which is "ich". Then "programming" is "Programmierung" or "Coding". But "Programmierung" is more formal. Alternatively, sometimes people say "ich liebe es zu programmieren" which is "I love to program". Hmm, maybe the direct translation would be "Ich liebe die Programmierung." But maybe the more natural way is "Ich liebe es zu programmieren." Let me check. Both are correct, but the second one might sound more natural in everyday speech. The user might prefer the concise version. Alternatively, maybe "Ich liebe die Programmierung." is better. Wait, the original is "programming" as a noun. So using the noun form would be appropriate. So "Ich liebe die Programmierung." But sometimes people also use "Coding" in German, like "Ich liebe das Coding." But that\'s more anglicism. Probably better to stick with "Programmierung". Alternatively, "Programmieren" as a noun. Oh right! "Programmieren" can be a noun when used in the accusative case. So "Ich liebe das Programmieren." That\'s correct and natural. Yes, that\'s the best translation. So the answer is "Ich liebe das Programmieren."'}, response_metadata={'model_name': 'qwq-plus'}, id='run-2c418451-51d8-4319-8269-2ce129363a1a-0', usage_metadata={'input_tokens': 28, 'output_tokens': 341, 'total_tokens': 369, 'input_token_details': {}, 'output_token_details': {}})
```

## Tool Calling

ChatQwQ supports tool calling API that lets you describe tools and their arguments, and have the model return a JSON object with a tool to invoke and the inputs to that tool.

### Use with `bind_tools`

```python
from langchain_core.tools import tool
from langchain_qwq import ChatQwQ


@tool
def multiply(first_int: int, second_int: int) -> int:
    """Multiply two integers together."""
    return first_int * second_int


llm = ChatQwQ()

llm_with_tools = llm.bind_tools([multiply])

msg = llm_with_tools.invoke("What's 5 times forty two")

print(msg)
```

```output
content='' additional_kwargs={'reasoning_content': 'Okay, the user is asking "What\'s 5 times forty two". Let me break this down. First, I need to identify the numbers involved. The first number is 5, which is straightforward. The second number is forty two, which is 42 in digits. The operation they want is multiplication.\n\nLooking at the tools provided, there\'s a function called multiply that takes two integers. So I should use that. The parameters are first_int and second_int. \n\nI need to convert "forty two" to 42. Since the function requires integers, both numbers should be in integer form. So 5 and 42. \n\nNow, I\'ll structure the tool call. The function name is multiply, and the arguments should be first_int: 5 and second_int: 42. I\'ll make sure the JSON is correctly formatted without any syntax errors. Let me double-check the parameters to ensure they\'re required and of the right type. Yep, both are required and integers. \n\nNo examples were provided, but the function\'s purpose is clear. So the correct tool call should be to multiply those two numbers. I think that\'s all. No other functions are needed here.'} response_metadata={'model_name': 'qwq-plus'} id='run-638895aa-fdde-4567-bcfa-7d8e5d4f24af-0' tool_calls=[{'name': 'multiply', 'args': {'first_int': 5, 'second_int': 42}, 'id': 'call_d088275851c140529ed2ad', 'type': 'tool_call'}] usage_metadata={'input_tokens': 176, 'output_tokens': 277, 'total_tokens': 453, 'input_token_details': {}, 'output_token_details': {}}
```

## API reference

For detailed documentation of all ChatQwQ features and configurations head to the [API reference](https://pypi.org/project/langchain-qwq/)
