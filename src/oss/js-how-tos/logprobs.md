# How to get log probabilities

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:

- [Chat models](/oss/concepts/chat_models)

</Info>

Certain chat models can be configured to return token-level log probabilities representing the likelihood of a given token. This guide walks through how to get this information in LangChain.

## OpenAI

Install the `@langchain/openai` package and set your API key:

```{=mdx}
import IntegrationInstallTooltip from "@mdx_components/integration_install_tooltip.mdx";
<IntegrationInstallTooltip></IntegrationInstallTooltip>

<Npm2Yarn>
  @langchain/openai @langchain/core
</Npm2Yarn>
```
For the OpenAI API to return log probabilities, we need to set the `logprobs` param to `true`. Then, the logprobs are included on each output [`AIMessage`](https://api.python.langchain.com/en/latest/messages/langchain_core.messages.ai.AIMessage.html) as part of the `response_metadata`:


```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({
  model: "gpt-4o",
  logprobs: true,
});

const responseMessage = await model.invoke("how are you today?");

responseMessage.response_metadata.logprobs.content.slice(0, 5);
```
```output
[
  {
    token: "Thank",
    logprob: -0.70174205,
    bytes: [ 84, 104, 97, 110, 107 ],
    top_logprobs: []
  },
  {
    token: " you",
    logprob: 0,
    bytes: [ 32, 121, 111, 117 ],
    top_logprobs: []
  },
  {
    token: " for",
    logprob: -0.000004723352,
    bytes: [ 32, 102, 111, 114 ],
    top_logprobs: []
  },
  {
    token: " asking",
    logprob: -0.0000013856493,
    bytes: [
       32,  97, 115,
      107, 105, 110,
      103
    ],
    top_logprobs: []
  },
  {
    token: "!",
    logprob: -0.00030102333,
    bytes: [ 33 ],
    top_logprobs: []
  }
]
```


And are part of streamed Message chunks as well:


```typescript
let count = 0;
const stream = await model.stream("How are you today?");
let aggregateResponse;

for await (const chunk of stream) {
  if (count > 5) {
    break;
  }
  if (aggregateResponse === undefined) {
    aggregateResponse = chunk;
  } else {
    aggregateResponse = aggregateResponse.concat(chunk);
  }
  console.log(aggregateResponse.response_metadata.logprobs?.content);
  count++;
}
```
```output
[]
[
  {
    token: "Thank",
    logprob: -0.23375113,
    bytes: [ 84, 104, 97, 110, 107 ],
    top_logprobs: []
  }
]
[
  {
    token: "Thank",
    logprob: -0.23375113,
    bytes: [ 84, 104, 97, 110, 107 ],
    top_logprobs: []
  },
  {
    token: " you",
    logprob: 0,
    bytes: [ 32, 121, 111, 117 ],
    top_logprobs: []
  }
]
[
  {
    token: "Thank",
    logprob: -0.23375113,
    bytes: [ 84, 104, 97, 110, 107 ],
    top_logprobs: []
  },
  {
    token: " you",
    logprob: 0,
    bytes: [ 32, 121, 111, 117 ],
    top_logprobs: []
  },
  {
    token: " for",
    logprob: -0.000004723352,
    bytes: [ 32, 102, 111, 114 ],
    top_logprobs: []
  }
]
[
  {
    token: "Thank",
    logprob: -0.23375113,
    bytes: [ 84, 104, 97, 110, 107 ],
    top_logprobs: []
  },
  {
    token: " you",
    logprob: 0,
    bytes: [ 32, 121, 111, 117 ],
    top_logprobs: []
  },
  {
    token: " for",
    logprob: -0.000004723352,
    bytes: [ 32, 102, 111, 114 ],
    top_logprobs: []
  },
  {
    token: " asking",
    logprob: -0.0000029352968,
    bytes: [
       32,  97, 115,
      107, 105, 110,
      103
    ],
    top_logprobs: []
  }
]
[
  {
    token: "Thank",
    logprob: -0.23375113,
    bytes: [ 84, 104, 97, 110, 107 ],
    top_logprobs: []
  },
  {
    token: " you",
    logprob: 0,
    bytes: [ 32, 121, 111, 117 ],
    top_logprobs: []
  },
  {
    token: " for",
    logprob: -0.000004723352,
    bytes: [ 32, 102, 111, 114 ],
    top_logprobs: []
  },
  {
    token: " asking",
    logprob: -0.0000029352968,
    bytes: [
       32,  97, 115,
      107, 105, 110,
      103
    ],
    top_logprobs: []
  },
  {
    token: "!",
    logprob: -0.00039694557,
    bytes: [ 33 ],
    top_logprobs: []
  }
]
```
## `topLogprobs`

To see alternate potential generations at each step, you can use the `topLogprobs` parameter:


```typescript
const modelWithTopLogprobs = new ChatOpenAI({
  model: "gpt-4o",
  logprobs: true,
  topLogprobs: 3,
});

const res = await modelWithTopLogprobs.invoke("how are you today?");

res.response_metadata.logprobs.content.slice(0, 5);
```



```output
[
  {
    token: "I'm",
    logprob: -2.2864406,
    bytes: [ 73, 39, 109 ],
    top_logprobs: [
      {
        token: "Thank",
        logprob: -0.28644064,
        bytes: [ 84, 104, 97, 110, 107 ]
      },
      {
        token: "Hello",
        logprob: -2.0364406,
        bytes: [ 72, 101, 108, 108, 111 ]
      },
      { token: "I'm", logprob: -2.2864406, bytes: [ 73, 39, 109 ] }
    ]
  },
  {
    token: " just",
    logprob: -0.14442946,
    bytes: [ 32, 106, 117, 115, 116 ],
    top_logprobs: [
      {
        token: " just",
        logprob: -0.14442946,
        bytes: [ 32, 106, 117, 115, 116 ]
      },
      { token: " an", logprob: -2.2694294, bytes: [ 32, 97, 110 ] },
      {
        token: " here",
        logprob: -4.0194297,
        bytes: [ 32, 104, 101, 114, 101 ]
      }
    ]
  },
  {
    token: " a",
    logprob: -0.00066632946,
    bytes: [ 32, 97 ],
    top_logprobs: [
      { token: " a", logprob: -0.00066632946, bytes: [ 32, 97 ] },
      {
        token: " lines",
        logprob: -7.750666,
        bytes: [ 32, 108, 105, 110, 101, 115 ]
      },
      { token: " an", logprob: -9.250667, bytes: [ 32, 97, 110 ] }
    ]
  },
  {
    token: " computer",
    logprob: -0.015423919,
    bytes: [
       32,  99, 111, 109,
      112, 117, 116, 101,
      114
    ],
    top_logprobs: [
      {
        token: " computer",
        logprob: -0.015423919,
        bytes: [
           32,  99, 111, 109,
          112, 117, 116, 101,
          114
        ]
      },
      {
        token: " program",
        logprob: -5.265424,
        bytes: [
           32, 112, 114, 111,
          103, 114,  97, 109
        ]
      },
      {
        token: " machine",
        logprob: -5.390424,
        bytes: [
           32, 109,  97,  99,
          104, 105, 110, 101
        ]
      }
    ]
  },
  {
    token: " program",
    logprob: -0.0010724656,
    bytes: [
       32, 112, 114, 111,
      103, 114,  97, 109
    ],
    top_logprobs: [
      {
        token: " program",
        logprob: -0.0010724656,
        bytes: [
           32, 112, 114, 111,
          103, 114,  97, 109
        ]
      },
      {
        token: "-based",
        logprob: -6.8760724,
        bytes: [ 45, 98, 97, 115, 101, 100 ]
      },
      {
        token: " algorithm",
        logprob: -10.626073,
        bytes: [
           32,  97, 108, 103,
          111, 114, 105, 116,
          104, 109
        ]
      }
    ]
  }
]
```


## Next steps

You've now learned how to get logprobs from OpenAI models in LangChain.

Next, check out the other how-to guides chat models in this section, like [how to get a model to return structured output](/oss/how-to/structured_output) or [how to track token usage](/oss/how-to/chat_token_usage_tracking).
