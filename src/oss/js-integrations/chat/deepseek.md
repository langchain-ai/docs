---
title: ChatDeepSeek
---


This will help you getting started with DeepSeek [chat models](/oss/concepts/#chat-models). For detailed documentation of all `ChatDeepSeek` features and configurations head to the [API reference](https://api.js.langchain.com/classes/_langchain_deepseek.ChatDeepSeek.html).

## Overview
### Integration details

| Class | Package | Local | Serializable | [PY support](https://python.langchain.com/docs/integrations/chat/deepseek) | Package downloads | Package latest |
| :--- | :--- | :---: | :---: |  :---: | :---: | :---: |
| [`ChatDeepSeek`](https://api.js.langchain.com/classes/_langchain_deepseek.ChatDeepSeek.html) | [`@langchain/deepseek`](https://npmjs.com/@langchain/deepseek) | ❌ (see [Ollama](/oss/integrations/chat/ollama)) | beta | ✅ | ![NPM - Downloads](https://img.shields.io/npm/dm/@langchain/deepseek?style=flat-square&label=%20&) | ![NPM - Version](https://img.shields.io/npm/v/@langchain/deepseek?style=flat-square&label=%20&) |

### Model features

See the links in the table headers below for guides on how to use specific features.

| [Tool calling](/oss/how-to/tool_calling) | [Structured output](/oss/how-to/structured_output/) | JSON mode | [Image input](/oss/how-to/multimodal_inputs/) | Audio input | Video input | [Token-level streaming](/oss/how-to/chat_streaming/) | [Token usage](/oss/how-to/chat_token_usage_tracking/) | [Logprobs](/oss/how-to/logprobs/) |
| :---: | :---: | :---: | :---: |  :---: | :---: | :---: | :---: | :---: |
| ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | 

Note that as of 1/27/25, tool calling and structured output are not currently supported for `deepseek-reasoner`.

## Setup

To access DeepSeek models you'll need to create a DeepSeek account, get an API key, and install the `@langchain/deepseek` integration package.

You can also access the DeepSeek API through providers like [Together AI](/oss/integrations/chat/togetherai) or [Ollama](/oss/integrations/chat/ollama).

### Credentials

Head to https://deepseek.com/ to sign up to DeepSeek and generate an API key. Once you've done this set the `DEEPSEEK_API_KEY` environment variable:

```bash
export DEEPSEEK_API_KEY="your-api-key"
```

If you want to get automated tracing of your model calls you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

```bash
# export LANGSMITH_TRACING="true"
# export LANGSMITH_API_KEY="your-api-key"
```

### Installation

The LangChain ChatDeepSeek integration lives in the `@langchain/deepseek` package:

```{=mdx}
import IntegrationInstallTooltip from "@mdx_components/integration_install_tooltip.mdx";
<IntegrationInstallTooltip></IntegrationInstallTooltip>

<Npm2Yarn>
  @langchain/deepseek @langchain/core
</Npm2Yarn>

```
## Instantiation

Now we can instantiate our model object and generate chat completions:


```typescript
import { ChatDeepSeek } from "@langchain/deepseek";

const llm = new ChatDeepSeek({
  model: "deepseek-reasoner",
  temperature: 0,
  // other params...
})
```
<!-- ## Invocation -->


```typescript
const aiMsg = await llm.invoke([
  [
    "system",
    "You are a helpful assistant that translates English to French. Translate the user sentence.",
  ],
  ["human", "I love programming."],
])
aiMsg
```
```output
AIMessage {
  "id": "e2874482-68a7-4552-8154-b6a245bab429",
  "content": "J'adore la programmation.",
  "additional_kwargs": {,
    "reasoning_content": "...",
  },
  "response_metadata": {
    "tokenUsage": {
      "promptTokens": 23,
      "completionTokens": 7,
      "totalTokens": 30
    },
    "finish_reason": "stop",
    "model_name": "deepseek-reasoner",
    "usage": {
      "prompt_tokens": 23,
      "completion_tokens": 7,
      "total_tokens": 30,
      "prompt_tokens_details": {
        "cached_tokens": 0
      },
      "prompt_cache_hit_tokens": 0,
      "prompt_cache_miss_tokens": 23
    },
    "system_fingerprint": "fp_3a5770e1b4"
  },
  "tool_calls": [],
  "invalid_tool_calls": [],
  "usage_metadata": {
    "output_tokens": 7,
    "input_tokens": 23,
    "total_tokens": 30,
    "input_token_details": {
      "cache_read": 0
    },
    "output_token_details": {}
  }
}
```

```typescript
console.log(aiMsg.content)
```
```output
J'adore la programmation.
```
## Chaining

We can [chain](/oss/how-to/sequence/) our model with a prompt template like so:


```typescript
import { ChatPromptTemplate } from "@langchain/core/prompts"

const prompt = ChatPromptTemplate.fromMessages(
  [
    [
      "system",
      "You are a helpful assistant that translates {input_language} to {output_language}.",
    ],
    ["human", "{input}"],
  ]
)

const chain = prompt.pipe(llm);
await chain.invoke(
  {
    input_language: "English",
    output_language: "German",
    input: "I love programming.",
  }
)
```
```output
AIMessage {
  "id": "6e7f6f8c-8d7a-4dad-be07-425384038fd4",
  "content": "Ich liebe es zu programmieren.",
  "additional_kwargs": {,
    "reasoning_content": "...",
  },
  "response_metadata": {
    "tokenUsage": {
      "promptTokens": 18,
      "completionTokens": 9,
      "totalTokens": 27
    },
    "finish_reason": "stop",
    "model_name": "deepseek-reasoner",
    "usage": {
      "prompt_tokens": 18,
      "completion_tokens": 9,
      "total_tokens": 27,
      "prompt_tokens_details": {
        "cached_tokens": 0
      },
      "prompt_cache_hit_tokens": 0,
      "prompt_cache_miss_tokens": 18
    },
    "system_fingerprint": "fp_3a5770e1b4"
  },
  "tool_calls": [],
  "invalid_tool_calls": [],
  "usage_metadata": {
    "output_tokens": 9,
    "input_tokens": 18,
    "total_tokens": 27,
    "input_token_details": {
      "cache_read": 0
    },
    "output_token_details": {}
  }
}
```
## API reference

For detailed documentation of all ChatDeepSeek features and configurations head to the API reference: https://api.js.langchain.com/classes/_langchain_deepseek.ChatDeepSeek.html
