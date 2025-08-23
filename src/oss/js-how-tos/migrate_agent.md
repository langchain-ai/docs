# How to migrate from legacy LangChain agents to LangGraph

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:
- [Agents](/oss/concepts/agents)
- [LangGraph.js](https://langchain-ai.github.io/langgraphjs/)
- [Tool calling](/oss/how-to/tool_calling/)

</Info>

Here we focus on how to move from legacy LangChain agents to more flexible [LangGraph](https://langchain-ai.github.io/langgraphjs/) agents.
LangChain agents (the
[`AgentExecutor`](https://api.js.langchain.com/classes/langchain.agents.AgentExecutor.html)
in particular) have multiple configuration parameters. In this notebook we will
show how those parameters map to the LangGraph
react agent executor using the [create_react_agent](https://langchain-ai.github.io/langgraphjs/reference/functions/prebuilt.createReactAgent.html) prebuilt helper method.

For more information on how to build agentic workflows in LangGraph, check out
the [docs here](https://langchain-ai.github.io/langgraphjs/how-tos/).

#### Prerequisites

This how-to guide uses OpenAI's `"gpt-4o-mini"` as the LLM. If you are running this guide as a notebook, set your OpenAI API key as shown below:


```typescript
// process.env.OPENAI_API_KEY = "...";

// Optional, add tracing in LangSmith
// process.env.LANGSMITH_API_KEY = "ls...";
// process.env.LANGCHAIN_CALLBACKS_BACKGROUND = "true";
// process.env.LANGSMITH_TRACING = "true";
// process.env.LANGSMITH_PROJECT = "How to migrate: LangGraphJS";

// Reduce tracing latency if you are not in a serverless environment
// process.env.LANGCHAIN_CALLBACKS_BACKGROUND = "true";
```

## Basic Usage

For basic creation and usage of a tool-calling ReAct-style agent, the
functionality is the same. First, let's define a model and tool(s), then we'll
use those to create an agent.

<Note>
**The `tool` function is available in `@langchain/core` version 0.2.7 and above.**


If you are on an older version of core, you should use instantiate and use [`DynamicStructuredTool`](https://api.js.langchain.com/classes/langchain_core.tools.DynamicStructuredTool.html) instead.
</Note>


```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { ChatOpenAI } from "@langchain/openai";

const llm = new ChatOpenAI({
  model: "gpt-4o-mini",
});

const magicTool = tool(async ({ input }: { input: number }) => {
  return `${input + 2}`;
}, {
  name: "magic_function",
  description: "Applies a magic function to an input.",
  schema: z.object({
    input: z.number(),
  }),
});

const tools = [magicTool];

const query = "what is the value of magic_function(3)?";
```

For the LangChain
[`AgentExecutor`](https://api.js.langchain.com/classes/langchain_agents.AgentExecutor.html),
we define a prompt with a placeholder for the agent's scratchpad. The agent can
be invoked as follows:



```typescript
import {
  ChatPromptTemplate,
} from "@langchain/core/prompts";
import { createToolCallingAgent } from "langchain/agents";
import { AgentExecutor } from "langchain/agents";

const prompt = ChatPromptTemplate.fromMessages([
  ["system", "You are a helpful assistant"],
  ["placeholder", "{chat_history}"],
  ["human", "{input}"],
  ["placeholder", "{agent_scratchpad}"],
]);

const agent = createToolCallingAgent({
  llm,
  tools,
  prompt
});
const agentExecutor = new AgentExecutor({
  agent,
  tools,
});

await agentExecutor.invoke({ input: query });
```



```output
{
  input: "what is the value of magic_function(3)?",
  output: "The value of `magic_function(3)` is 5."
}
```


LangGraph's off-the-shelf
[react agent executor](https://langchain-ai.github.io/langgraphjs/reference/functions/prebuilt.createReactAgent.html)
manages a state that is defined by a list of messages. In a similar way to the `AgentExecutor`, it will continue to
process the list until there are no tool calls in the agent's output. To kick it
off, we input a list of messages. The output will contain the entire state of
the graph - in this case, the conversation history and messages representing intermediate tool calls:



```typescript
import { createReactAgent } from "@langchain/langgraph/prebuilt";

const app = createReactAgent({
  llm,
  tools,
});

let agentOutput = await app.invoke({
  messages: [
    {
      role: "user",
      content: query
    },
  ],
});

console.log(agentOutput);
```
```output
{
  messages: [
    HumanMessage {
      "id": "eeef343c-80d1-4ccb-86af-c109343689cd",
      "content": "what is the value of magic_function(3)?",
      "additional_kwargs": {},
      "response_metadata": {}
    },
    AIMessage {
      "id": "chatcmpl-A7exs2uRqEipaZ7MtRbXnqu0vT0Da",
      "content": "",
      "additional_kwargs": {
        "tool_calls": [
          {
            "id": "call_MtwWLn000BQHeSYQKsbxYNR0",
            "type": "function",
            "function": "[Object]"
          }
        ]
      },
      "response_metadata": {
        "tokenUsage": {
          "completionTokens": 14,
          "promptTokens": 55,
          "totalTokens": 69
        },
        "finish_reason": "tool_calls",
        "system_fingerprint": "fp_483d39d857"
      },
      "tool_calls": [
        {
          "name": "magic_function",
          "args": {
            "input": 3
          },
          "type": "tool_call",
          "id": "call_MtwWLn000BQHeSYQKsbxYNR0"
        }
      ],
      "invalid_tool_calls": [],
      "usage_metadata": {
        "input_tokens": 55,
        "output_tokens": 14,
        "total_tokens": 69
      }
    },
    ToolMessage {
      "id": "1001bf20-7cde-4f8b-81f1-1faa654a8bb4",
      "content": "5",
      "name": "magic_function",
      "additional_kwargs": {},
      "response_metadata": {},
      "tool_call_id": "call_MtwWLn000BQHeSYQKsbxYNR0"
    },
    AIMessage {
      "id": "chatcmpl-A7exsTk3ilzGzC8DuY8GpnKOaGdvx",
      "content": "The value of `magic_function(3)` is 5.",
      "additional_kwargs": {},
      "response_metadata": {
        "tokenUsage": {
          "completionTokens": 14,
          "promptTokens": 78,
          "totalTokens": 92
        },
        "finish_reason": "stop",
        "system_fingerprint": "fp_54e2f484be"
      },
      "tool_calls": [],
      "invalid_tool_calls": [],
      "usage_metadata": {
        "input_tokens": 78,
        "output_tokens": 14,
        "total_tokens": 92
      }
    }
  ]
}
```

```typescript
const messageHistory = agentOutput.messages;
const newQuery = "Pardon?";

agentOutput = await app.invoke({
  messages: [
    ...messageHistory,
    { role: "user", content: newQuery }
  ],
});

```



```output
{
  messages: [
    HumanMessage {
      "id": "eeef343c-80d1-4ccb-86af-c109343689cd",
      "content": "what is the value of magic_function(3)?",
      "additional_kwargs": {},
      "response_metadata": {}
    },
    AIMessage {
      "id": "chatcmpl-A7exs2uRqEipaZ7MtRbXnqu0vT0Da",
      "content": "",
      "additional_kwargs": {
        "tool_calls": [
          {
            "id": "call_MtwWLn000BQHeSYQKsbxYNR0",
            "type": "function",
            "function": "[Object]"
          }
        ]
      },
      "response_metadata": {
        "tokenUsage": {
          "completionTokens": 14,
          "promptTokens": 55,
          "totalTokens": 69
        },
        "finish_reason": "tool_calls",
        "system_fingerprint": "fp_483d39d857"
      },
      "tool_calls": [
        {
          "name": "magic_function",
          "args": {
            "input": 3
          },
          "type": "tool_call",
          "id": "call_MtwWLn000BQHeSYQKsbxYNR0"
        }
      ],
      "invalid_tool_calls": [],
      "usage_metadata": {
        "input_tokens": 55,
        "output_tokens": 14,
        "total_tokens": 69
      }
    },
    ToolMessage {
      "id": "1001bf20-7cde-4f8b-81f1-1faa654a8bb4",
      "content": "5",
      "name": "magic_function",
      "additional_kwargs": {},
      "response_metadata": {},
      "tool_call_id": "call_MtwWLn000BQHeSYQKsbxYNR0"
    },
    AIMessage {
      "id": "chatcmpl-A7exsTk3ilzGzC8DuY8GpnKOaGdvx",
      "content": "The value of `magic_function(3)` is 5.",
      "additional_kwargs": {},
      "response_metadata": {
        "tokenUsage": {
          "completionTokens": 14,
          "promptTokens": 78,
          "totalTokens": 92
        },
        "finish_reason": "stop",
        "system_fingerprint": "fp_54e2f484be"
      },
      "tool_calls": [],
      "invalid_tool_calls": [],
      "usage_metadata": {
        "input_tokens": 78,
        "output_tokens": 14,
        "total_tokens": 92
      }
    },
    HumanMessage {
      "id": "1f2a9f41-c8ff-48fe-9d93-e663ee9279ff",
      "content": "Pardon?",
      "additional_kwargs": {},
      "response_metadata": {}
    },
    AIMessage {
      "id": "chatcmpl-A7exyTe9Ofs63Ex3sKwRx3wWksNup",
      "content": "The result of calling the `magic_function` with an input of 3 is 5.",
      "additional_kwargs": {},
      "response_metadata": {
        "tokenUsage": {
          "completionTokens": 20,
          "promptTokens": 102,
          "totalTokens": 122
        },
        "finish_reason": "stop",
        "system_fingerprint": "fp_483d39d857"
      },
      "tool_calls": [],
      "invalid_tool_calls": [],
      "usage_metadata": {
        "input_tokens": 102,
        "output_tokens": 20,
        "total_tokens": 122
      }
    }
  ]
}
```


## Prompt Templates

With legacy LangChain agents you have to pass in a prompt template. You can use
this to control the agent.

With LangGraph
[react agent executor](https://langchain-ai.github.io/langgraphjs/reference/functions/prebuilt.createReactAgent.html),
by default there is no prompt. You can achieve similar control over the agent in
a few ways:

1. Pass in a system message as input
2. Initialize the agent with a system message
3. Initialize the agent with a function to transform messages before passing to
   the model.

Let's take a look at all of these below. We will pass in custom instructions to
get the agent to respond in Spanish.

First up, using LangChain's `AgentExecutor`:



```typescript
const spanishPrompt = ChatPromptTemplate.fromMessages([
  ["system", "You are a helpful assistant. Respond only in Spanish."],
  ["placeholder", "{chat_history}"],
  ["human", "{input}"],
  ["placeholder", "{agent_scratchpad}"],
]);

const spanishAgent = createToolCallingAgent({
  llm,
  tools,
  prompt: spanishPrompt,
});
const spanishAgentExecutor = new AgentExecutor({
  agent: spanishAgent,
  tools,
});

await spanishAgentExecutor.invoke({ input: query });

```



```output
{
  input: "what is the value of magic_function(3)?",
  output: "El valor de `magic_function(3)` es 5."
}
```


Now, let's pass a custom system message to [react agent executor](https://langchain-ai.github.io/langgraphjs/reference/functions/prebuilt.createReactAgent.html).

LangGraph's prebuilt `create_react_agent` does not take a prompt template directly as a parameter, but instead takes a `messages_modifier` parameter. This modifies messages before they are passed into the model, and can be one of four values:

- A `SystemMessage`, which is added to the beginning of the list of messages.
- A `string`, which is converted to a `SystemMessage` and added to the beginning of the list of messages.
- A `Callable`, which should take in a list of messages. The output is then passed to the language model.
- Or a [`Runnable`](/oss/concepts/lcel), which should should take in a list of messages. The output is then passed to the language model.

Here's how it looks in action:



```typescript
const systemMessage = "You are a helpful assistant. Respond only in Spanish.";

// This could also be a SystemMessage object
// const systemMessage = new SystemMessage("You are a helpful assistant. Respond only in Spanish.");

const appWithSystemMessage = createReactAgent({
  llm,
  tools,
  messageModifier: systemMessage,
});

agentOutput = await appWithSystemMessage.invoke({
  messages: [
    { role: "user", content: query }
  ],
});
agentOutput.messages[agentOutput.messages.length - 1];
```



```output
AIMessage {
  "id": "chatcmpl-A7ey8LGWAs8ldrRRcO5wlHM85w9T8",
  "content": "El valor de `magic_function(3)` es 5.",
  "additional_kwargs": {},
  "response_metadata": {
    "tokenUsage": {
      "completionTokens": 14,
      "promptTokens": 89,
      "totalTokens": 103
    },
    "finish_reason": "stop",
    "system_fingerprint": "fp_483d39d857"
  },
  "tool_calls": [],
  "invalid_tool_calls": [],
  "usage_metadata": {
    "input_tokens": 89,
    "output_tokens": 14,
    "total_tokens": 103
  }
}
```


We can also pass in an arbitrary function. This function should take in a list
of messages and output a list of messages. We can do all types of arbitrary
formatting of messages here. In this cases, let's just add a `SystemMessage` to
the start of the list of messages.



```typescript
import { BaseMessage, SystemMessage, HumanMessage } from "@langchain/core/messages";

const modifyMessages = (messages: BaseMessage[]) => {
  return [
    new SystemMessage("You are a helpful assistant. Respond only in Spanish."),
    ...messages,
    new HumanMessage("Also say 'Pandemonium!' after the answer."),
  ];
};

const appWithMessagesModifier = createReactAgent({
  llm,
  tools,
  messageModifier: modifyMessages,
});

agentOutput = await appWithMessagesModifier.invoke({
  messages: [{ role: "user", content: query }],
});

console.log({
  input: query,
  output: agentOutput.messages[agentOutput.messages.length - 1].content,
});
```
```output
{
  input: "what is the value of magic_function(3)?",
  output: "El valor de magic_function(3) es 5. ¡Pandemonium!"
}
```
## Memory

With LangChain's
[`AgentExecutor`](https://api.js.langchain.com/classes/langchain_agents.AgentExecutor.html), you could add chat memory classes so it can engage in a multi-turn conversation.



```typescript
import { ChatMessageHistory } from "@langchain/community/stores/message/in_memory";
import { RunnableWithMessageHistory } from "@langchain/core/runnables";

const memory = new ChatMessageHistory();
const agentExecutorWithMemory = new RunnableWithMessageHistory({
  runnable: agentExecutor,
  getMessageHistory: () => memory,
  inputMessagesKey: "input",
  historyMessagesKey: "chat_history",
});

const config = { configurable: { sessionId: "test-session" } };

agentOutput = await agentExecutorWithMemory.invoke(
  { input: "Hi, I'm polly! What's the output of magic_function of 3?" },
  config,
);

console.log(agentOutput.output);

agentOutput = await agentExecutorWithMemory.invoke(
  { input: "Remember my name?" },
  config,
);

console.log("---");
console.log(agentOutput.output);
console.log("---");

agentOutput = await agentExecutorWithMemory.invoke(
  { input: "what was that output again?" },
  config,
);

console.log(agentOutput.output);
```
```output
The output of the magic function for the input 3 is 5.
---
Yes, your name is Polly! How can I assist you today?
---
The output of the magic function for the input 3 is 5.
```
#### In LangGraph

The equivalent to this type of memory in LangGraph is [persistence](https://langchain-ai.github.io/langgraphjs/how-tos/persistence/), and [checkpointing](https://langchain-ai.github.io/langgraphjs/reference/interfaces/index.Checkpoint.html).

Add a `checkpointer` to the agent and you get chat memory for free. You'll need to also pass a `thread_id` within the `configurable` field in the `config` parameter. Notice that we only pass one message into each request, but the model still has context from previous runs:


```typescript
import { MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();
const appWithMemory = createReactAgent({
  llm: llm,
  tools: tools,
  checkpointSaver: checkpointer
});

const langGraphConfig = {
  configurable: {
    thread_id: "test-thread",
  },
};

agentOutput = await appWithMemory.invoke(
  {
    messages: [
      {
        role: "user",
        content: "Hi, I'm polly! What's the output of magic_function of 3?",
      }
    ],
  },
  langGraphConfig,
);

console.log(agentOutput.messages[agentOutput.messages.length - 1].content);
console.log("---");

agentOutput = await appWithMemory.invoke(
  {
    messages: [
      { role: "user", content: "Remember my name?" }
    ]
  },
  langGraphConfig,
);

console.log(agentOutput.messages[agentOutput.messages.length - 1].content);
console.log("---");

agentOutput = await appWithMemory.invoke(
  {
    messages: [
      { role: "user", content: "what was that output again?" }
    ]
  },
  langGraphConfig,
);

console.log(agentOutput.messages[agentOutput.messages.length - 1].content);
```
```output
Hi Polly! The output of the magic function for the input 3 is 5.
---
Yes, your name is Polly!
---
The output of the magic function for the input 3 was 5.
```
## Iterating through steps

With LangChain's
[`AgentExecutor`](https://api.js.langchain.com/classes/langchain_agents.AgentExecutor.html),
you could iterate over the steps using the
[`stream`](https://api.js.langchain.com/classes/langchain_core.runnables.Runnable.html#stream) method:



```typescript
const langChainStream = await agentExecutor.stream({ input: query });

for await (const step of langChainStream) {
  console.log(step);
}
```
```output
{
  intermediateSteps: [
    {
      action: {
        tool: "magic_function",
        toolInput: { input: 3 },
        toolCallId: "call_IQZr1yy2Ug6904VkQg6pWGgR",
        log: 'Invoking "magic_function" with {"input":3}\n',
        messageLog: [
          AIMessageChunk {
            "id": "chatcmpl-A7eziUrDmLSSMoiOskhrfbsHqx4Sd",
            "content": "",
            "additional_kwargs": {
              "tool_calls": [
                {
                  "index": 0,
                  "id": "call_IQZr1yy2Ug6904VkQg6pWGgR",
                  "type": "function",
                  "function": "[Object]"
                }
              ]
            },
            "response_metadata": {
              "prompt": 0,
              "completion": 0,
              "finish_reason": "tool_calls",
              "system_fingerprint": "fp_483d39d857"
            },
            "tool_calls": [
              {
                "name": "magic_function",
                "args": {
                  "input": 3
                },
                "id": "call_IQZr1yy2Ug6904VkQg6pWGgR",
                "type": "tool_call"
              }
            ],
            "tool_call_chunks": [
              {
                "name": "magic_function",
                "args": "{\"input\":3}",
                "id": "call_IQZr1yy2Ug6904VkQg6pWGgR",
                "index": 0,
                "type": "tool_call_chunk"
              }
            ],
            "invalid_tool_calls": [],
            "usage_metadata": {
              "input_tokens": 61,
              "output_tokens": 14,
              "total_tokens": 75
            }
          }
        ]
      },
      observation: "5"
    }
  ]
}
{ output: "The value of `magic_function(3)` is 5." }
```
#### In LangGraph

In LangGraph, things are handled natively using the stream method.



```typescript
const langGraphStream = await app.stream(
  { messages: [{ role: "user", content: query }] },
  { streamMode: "updates" },
);

for await (const step of langGraphStream) {
  console.log(step);
}
```
```output
{
  agent: {
    messages: [
      AIMessage {
        "id": "chatcmpl-A7ezu8hirCENjdjR2GpLjkzXFTEmp",
        "content": "",
        "additional_kwargs": {
          "tool_calls": [
            {
              "id": "call_KhhNL0m3mlPoJiboFMoX8hzk",
              "type": "function",
              "function": "[Object]"
            }
          ]
        },
        "response_metadata": {
          "tokenUsage": {
            "completionTokens": 14,
            "promptTokens": 55,
            "totalTokens": 69
          },
          "finish_reason": "tool_calls",
          "system_fingerprint": "fp_483d39d857"
        },
        "tool_calls": [
          {
            "name": "magic_function",
            "args": {
              "input": 3
            },
            "type": "tool_call",
            "id": "call_KhhNL0m3mlPoJiboFMoX8hzk"
          }
        ],
        "invalid_tool_calls": [],
        "usage_metadata": {
          "input_tokens": 55,
          "output_tokens": 14,
          "total_tokens": 69
        }
      }
    ]
  }
}
{
  tools: {
    messages: [
      ToolMessage {
        "content": "5",
        "name": "magic_function",
        "additional_kwargs": {},
        "response_metadata": {},
        "tool_call_id": "call_KhhNL0m3mlPoJiboFMoX8hzk"
      }
    ]
  }
}
{
  agent: {
    messages: [
      AIMessage {
        "id": "chatcmpl-A7ezuTrh8GC550eKa1ZqRZGjpY5zh",
        "content": "The value of `magic_function(3)` is 5.",
        "additional_kwargs": {},
        "response_metadata": {
          "tokenUsage": {
            "completionTokens": 14,
            "promptTokens": 78,
            "totalTokens": 92
          },
          "finish_reason": "stop",
          "system_fingerprint": "fp_483d39d857"
        },
        "tool_calls": [],
        "invalid_tool_calls": [],
        "usage_metadata": {
          "input_tokens": 78,
          "output_tokens": 14,
          "total_tokens": 92
        }
      }
    ]
  }
}
```
## `returnIntermediateSteps`

Setting this parameter on AgentExecutor allows users to access
intermediate_steps, which pairs agent actions (e.g., tool invocations) with
their outcomes.


```typescript
const agentExecutorWithIntermediateSteps = new AgentExecutor({
  agent,
  tools,
  returnIntermediateSteps: true,
});

const result = await agentExecutorWithIntermediateSteps.invoke({
  input: query,
});

console.log(result.intermediateSteps);

```
```output
[
  {
    action: {
      tool: "magic_function",
      toolInput: { input: 3 },
      toolCallId: "call_mbg1xgLEYEEWClbEaDe7p5tK",
      log: 'Invoking "magic_function" with {"input":3}\n',
      messageLog: [
        AIMessageChunk {
          "id": "chatcmpl-A7f0NdSRSUJsBP6ENTpiQD4LzpBAH",
          "content": "",
          "additional_kwargs": {
            "tool_calls": [
              {
                "index": 0,
                "id": "call_mbg1xgLEYEEWClbEaDe7p5tK",
                "type": "function",
                "function": "[Object]"
              }
            ]
          },
          "response_metadata": {
            "prompt": 0,
            "completion": 0,
            "finish_reason": "tool_calls",
            "system_fingerprint": "fp_54e2f484be"
          },
          "tool_calls": [
            {
              "name": "magic_function",
              "args": {
                "input": 3
              },
              "id": "call_mbg1xgLEYEEWClbEaDe7p5tK",
              "type": "tool_call"
            }
          ],
          "tool_call_chunks": [
            {
              "name": "magic_function",
              "args": "{\"input\":3}",
              "id": "call_mbg1xgLEYEEWClbEaDe7p5tK",
              "index": 0,
              "type": "tool_call_chunk"
            }
          ],
          "invalid_tool_calls": [],
          "usage_metadata": {
            "input_tokens": 61,
            "output_tokens": 14,
            "total_tokens": 75
          }
        }
      ]
    },
    observation: "5"
  }
]
```
By default the
[react agent executor](https://langchain-ai.github.io/langgraphjs/reference/functions/prebuilt.createReactAgent.html)
in LangGraph appends all messages to the central state. Therefore, it is easy to
see any intermediate steps by just looking at the full state.



```typescript
agentOutput = await app.invoke({
  messages: [
    { role: "user", content: query },
  ]
});

console.log(agentOutput.messages);
```
```output
[
  HumanMessage {
    "id": "46a825b2-13a3-4f19-b1aa-7716c53eb247",
    "content": "what is the value of magic_function(3)?",
    "additional_kwargs": {},
    "response_metadata": {}
  },
  AIMessage {
    "id": "chatcmpl-A7f0iUuWktC8gXztWZCjofqyCozY2",
    "content": "",
    "additional_kwargs": {
      "tool_calls": [
        {
          "id": "call_ndsPDU58wsMeGaqr41cSlLlF",
          "type": "function",
          "function": "[Object]"
        }
      ]
    },
    "response_metadata": {
      "tokenUsage": {
        "completionTokens": 14,
        "promptTokens": 55,
        "totalTokens": 69
      },
      "finish_reason": "tool_calls",
      "system_fingerprint": "fp_483d39d857"
    },
    "tool_calls": [
      {
        "name": "magic_function",
        "args": {
          "input": 3
        },
        "type": "tool_call",
        "id": "call_ndsPDU58wsMeGaqr41cSlLlF"
      }
    ],
    "invalid_tool_calls": [],
    "usage_metadata": {
      "input_tokens": 55,
      "output_tokens": 14,
      "total_tokens": 69
    }
  },
  ToolMessage {
    "id": "ac6aa309-bbfb-46cd-ba27-cbdbfd848705",
    "content": "5",
    "name": "magic_function",
    "additional_kwargs": {},
    "response_metadata": {},
    "tool_call_id": "call_ndsPDU58wsMeGaqr41cSlLlF"
  },
  AIMessage {
    "id": "chatcmpl-A7f0i7iHyDUV6is6sgwtcXivmFZ1x",
    "content": "The value of `magic_function(3)` is 5.",
    "additional_kwargs": {},
    "response_metadata": {
      "tokenUsage": {
        "completionTokens": 14,
        "promptTokens": 78,
        "totalTokens": 92
      },
      "finish_reason": "stop",
      "system_fingerprint": "fp_54e2f484be"
    },
    "tool_calls": [],
    "invalid_tool_calls": [],
    "usage_metadata": {
      "input_tokens": 78,
      "output_tokens": 14,
      "total_tokens": 92
    }
  }
]
```
## `maxIterations`

`AgentExecutor` implements a `maxIterations` parameter, whereas this is
controlled via `recursionLimit` in LangGraph.

Note that in the LangChain `AgentExecutor`, an "iteration" includes a full turn of tool
invocation and execution. In LangGraph, each step contributes to the recursion
limit, so we will need to multiply by two (and add one) to get equivalent
results.

Here's an example of how you'd set this parameter with the legacy `AgentExecutor`:


```typescript
const badMagicTool = tool(async ({ input: _input }) => {
  return "Sorry, there was a temporary error. Please try again with the same input.";
}, {
  name: "magic_function",
  description: "Applies a magic function to an input.",
  schema: z.object({
    input: z.string(),
  }),
});

const badTools = [badMagicTool];

const spanishAgentExecutorWithMaxIterations = new AgentExecutor({
  agent: createToolCallingAgent({
    llm,
    tools: badTools,
    prompt: spanishPrompt,
  }),
  tools: badTools,
  verbose: true,
  maxIterations: 2,
});

await spanishAgentExecutorWithMaxIterations.invoke({ input: query });
```

If the recursion limit is reached in LangGraph.js, the framework will raise a specific exception type that we can catch and manage similarly to AgentExecutor.


```typescript
import { GraphRecursionError } from "@langchain/langgraph";

const RECURSION_LIMIT = 2 * 2 + 1;

const appWithBadTools = createReactAgent({ llm, tools: badTools });

try {
  await appWithBadTools.invoke({
    messages: [
      { role: "user", content: query }
    ]
  }, {
    recursionLimit: RECURSION_LIMIT,
  });
} catch (e) {
  if (e instanceof GraphRecursionError) {
    console.log("Recursion limit reached.");
  } else {
    throw e;
  }
}
```
```output
Recursion limit reached.
```
## Next steps

You've now learned how to migrate your LangChain agent executors to LangGraph.

Next, check out other [LangGraph how-to guides](https://langchain-ai.github.io/langgraphjs/how-tos/).
