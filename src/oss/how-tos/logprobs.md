# How to get log probabilities

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:
- [Chat models](/oss/concepts/chat_models)
- [Tokens](/oss/concepts/tokens)

</Info>

Certain [chat models](/oss/concepts/chat_models/) can be configured to return token-level log probabilities representing the likelihood of a given token. This guide walks through how to get this information in LangChain.

## OpenAI

Install the LangChain x OpenAI package and set your API key


```python
%pip install -qU langchain-openai
```


```python
import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass()
```

For the OpenAI API to return log probabilities we need to configure the `logprobs=True` param. Then, the logprobs are included on each output [`AIMessage`](https://python.langchain.com/api_reference/core/messages/langchain_core.messages.ai.AIMessage.html) as part of the `response_metadata`:


```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini").bind(logprobs=True)

msg = llm.invoke(("human", "how are you today"))

msg.response_metadata["logprobs"]["content"][:5]
```



```output
[{'token': 'I', 'bytes': [73], 'logprob': -0.26341408, 'top_logprobs': []},
 {'token': "'m",
  'bytes': [39, 109],
  'logprob': -0.48584133,
  'top_logprobs': []},
 {'token': ' just',
  'bytes': [32, 106, 117, 115, 116],
  'logprob': -0.23484154,
  'top_logprobs': []},
 {'token': ' a',
  'bytes': [32, 97],
  'logprob': -0.0018291725,
  'top_logprobs': []},
 {'token': ' computer',
  'bytes': [32, 99, 111, 109, 112, 117, 116, 101, 114],
  'logprob': -0.052299336,
  'top_logprobs': []}]
```


And are part of streamed Message chunks as well:


```python
ct = 0
full = None
for chunk in llm.stream(("human", "how are you today")):
    if ct < 5:
        full = chunk if full is None else full + chunk
        if "logprobs" in full.response_metadata:
            print(full.response_metadata["logprobs"]["content"])
    else:
        break
    ct += 1
```
```output
[]
[{'token': 'I', 'bytes': [73], 'logprob': -0.26593843, 'top_logprobs': []}]
[{'token': 'I', 'bytes': [73], 'logprob': -0.26593843, 'top_logprobs': []}, {'token': "'m", 'bytes': [39, 109], 'logprob': -0.3238896, 'top_logprobs': []}]
[{'token': 'I', 'bytes': [73], 'logprob': -0.26593843, 'top_logprobs': []}, {'token': "'m", 'bytes': [39, 109], 'logprob': -0.3238896, 'top_logprobs': []}, {'token': ' just', 'bytes': [32, 106, 117, 115, 116], 'logprob': -0.23778509, 'top_logprobs': []}]
[{'token': 'I', 'bytes': [73], 'logprob': -0.26593843, 'top_logprobs': []}, {'token': "'m", 'bytes': [39, 109], 'logprob': -0.3238896, 'top_logprobs': []}, {'token': ' just', 'bytes': [32, 106, 117, 115, 116], 'logprob': -0.23778509, 'top_logprobs': []}, {'token': ' a', 'bytes': [32, 97], 'logprob': -0.0022134194, 'top_logprobs': []}]
```
## Next steps

You've now learned how to get logprobs from OpenAI models in LangChain.

Next, check out the other how-to guides chat models in this section, like [how to get a model to return structured output](/oss/how-to/structured_output) or [how to track token usage](/oss/how-to/chat_token_usage_tracking).
