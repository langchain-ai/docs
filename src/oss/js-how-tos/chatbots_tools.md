# How to add tools to chatbots

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:

- [Chatbots](/oss/concepts/messages)
- [Agents](https://langchain-ai.github.io/langgraphjs/tutorials/multi_agent/agent_supervisor/)
- [Chat history](/oss/concepts/chat_history)

</Info>

This section will cover how to create conversational agents: chatbots that can interact with other systems and APIs using tools.

<Note>
**This how-to guide previously built a chatbot using [RunnableWithMessageHistory](https://api.js.langchain.com/classes/_langchain_core.runnables.RunnableWithMessageHistory.html). You can access this version of the tutorial in the [v0.2 docs](https://js.langchain.com/v0.2/docs/how_to/chatbots_tools/).**


The LangGraph implementation offers a number of advantages over `RunnableWithMessageHistory`, including the ability to persist arbitrary components of an application's state (instead of only messages).

</Note>

## Setup

For this guide, we'll be using a [tool calling agent](https://langchain-ai.github.io/langgraphjs/concepts/agentic_concepts/#tool-calling-agent) with a single tool for searching the web. The default will be powered by [Tavily](/oss/integrations/tools/tavily_search), but you can switch it out for any similar tool. The rest of this section will assume you're using Tavily.

You'll need to [sign up for an account](https://tavily.com/) on the Tavily website, and install the following packages:

```{=mdx}
<Npm2Yarn>
  @langchain/core @langchain/langgraph @langchain/community
</Npm2Yarn>
```
Let’s also set up a chat model that we’ll use for the below examples.

```{=mdx}
<ChatModelTabs customVarName="llm" />
```
```typescript
process.env.TAVILY_API_KEY = "YOUR_API_KEY";
```

## Creating an agent

Our end goal is to create an agent that can respond conversationally to user questions while looking up information as needed.

First, let's initialize Tavily and an OpenAI chat model capable of tool calling:


```typescript
// @lc-docs-hide-cell

import { ChatOpenAI } from "@langchain/openai";

const llm = new ChatOpenAI({
  model: "gpt-4o",
  temperature: 0,
});
```


```typescript
import { TavilySearchResults } from "@langchain/community/tools/tavily_search";

const tools = [
  new TavilySearchResults({
    maxResults: 1,
  }),
];
```

To make our agent conversational, we can also specify a prompt. Here's an example:


```typescript
import {
  ChatPromptTemplate,
} from "@langchain/core/prompts";

// Adapted from https://smith.langchain.com/hub/jacob/tool-calling-agent
const prompt = ChatPromptTemplate.fromMessages([
  [
    "system",
    "You are a helpful assistant. You may not need to use tools for every query - the user may just want to chat!",
  ],
]);
```

Great! Now let's assemble our agent using LangGraph's prebuilt [createReactAgent](https://langchain-ai.github.io/langgraphjs/reference/functions/langgraph_prebuilt.createReactAgent.html), which allows you to create a [tool-calling agent](https://langchain-ai.github.io/langgraphjs/concepts/agentic_concepts/#tool-calling-agent):


```typescript
import { createReactAgent } from "@langchain/langgraph/prebuilt"

// messageModifier allows you to preprocess the inputs to the model inside ReAct agent
// in this case, since we're passing a prompt string, we'll just always add a SystemMessage
// with this prompt string before any other messages sent to the model
const agent = createReactAgent({ llm, tools, messageModifier: prompt })
```

## Running the agent

Now that we've set up our agent, let's try interacting with it! It can handle both trivial queries that require no lookup:


```typescript
await agent.invoke({ messages: [{ role: "user", content: "I'm Nemo!" }]})
```
```output
{
  messages: [
    HumanMessage {
      "id": "8c5fa465-e8d8-472a-9434-f574bf74537f",
      "content": "I'm Nemo!",
      "additional_kwargs": {},
      "response_metadata": {}
    },
    AIMessage {
      "id": "chatcmpl-ABTKLLriRcZin65zLAMB3WUf9Sg1t",
      "content": "How can I assist you today?",
      "additional_kwargs": {},
      "response_metadata": {
        "tokenUsage": {
          "completionTokens": 8,
          "promptTokens": 93,
          "totalTokens": 101
        },
        "finish_reason": "stop",
        "system_fingerprint": "fp_3537616b13"
      },
      "tool_calls": [],
      "invalid_tool_calls": [],
      "usage_metadata": {
        "input_tokens": 93,
        "output_tokens": 8,
        "total_tokens": 101
      }
    }
  ]
}
```
Or, it can use of the passed search tool to get up to date information if needed:


```typescript
await agent.invoke({ messages: [{ role: "user", content: "What is the current conservation status of the Great Barrier Reef?" }]})
```
```output
{
  messages: [
    HumanMessage {
      "id": "65c315b6-2433-4cb1-97c7-b60b5546f518",
      "content": "What is the current conservation status of the Great Barrier Reef?",
      "additional_kwargs": {},
      "response_metadata": {}
    },
    AIMessage {
      "id": "chatcmpl-ABTKLQn1e4axRhqIhpKMyzWWTGauO",
      "content": "How can I assist you today?",
      "additional_kwargs": {},
      "response_metadata": {
        "tokenUsage": {
          "completionTokens": 8,
          "promptTokens": 93,
          "totalTokens": 101
        },
        "finish_reason": "stop",
        "system_fingerprint": "fp_3537616b13"
      },
      "tool_calls": [],
      "invalid_tool_calls": [],
      "usage_metadata": {
        "input_tokens": 93,
        "output_tokens": 8,
        "total_tokens": 101
      }
    }
  ]
}
```
## Conversational responses

Because our prompt contains a placeholder for chat history messages, our agent can also take previous interactions into account and respond conversationally like a standard chatbot:


```typescript
await agent.invoke({
  messages: [
    { role: "user", content: "I'm Nemo!" },
    { role: "user", content: "Hello Nemo! How can I assist you today?" },
    { role: "user", content: "What is my name?" }
  ]
})
```
```output
{
  messages: [
    HumanMessage {
      "id": "6433afc5-31bd-44b3-b34c-f11647e1677d",
      "content": "I'm Nemo!",
      "additional_kwargs": {},
      "response_metadata": {}
    },
    HumanMessage {
      "id": "f163b5f1-ea29-4d7a-9965-7c7c563d9cea",
      "content": "Hello Nemo! How can I assist you today?",
      "additional_kwargs": {},
      "response_metadata": {}
    },
    HumanMessage {
      "id": "382c3354-d02b-4888-98d8-44d75d045044",
      "content": "What is my name?",
      "additional_kwargs": {},
      "response_metadata": {}
    },
    AIMessage {
      "id": "chatcmpl-ABTKMKu7ThZDZW09yMIPTq2N723Cj",
      "content": "How can I assist you today?",
      "additional_kwargs": {},
      "response_metadata": {
        "tokenUsage": {
          "completionTokens": 8,
          "promptTokens": 93,
          "totalTokens": 101
        },
        "finish_reason": "stop",
        "system_fingerprint": "fp_e375328146"
      },
      "tool_calls": [],
      "invalid_tool_calls": [],
      "usage_metadata": {
        "input_tokens": 93,
        "output_tokens": 8,
        "total_tokens": 101
      }
    }
  ]
}
```
If preferred, you can also add memory to the LangGraph agent to manage the history of messages. Let's redeclare it this way:


```typescript
import { MemorySaver } from "@langchain/langgraph"

// highlight-start
const memory = new MemorySaver()
const agent2 = createReactAgent({ llm, tools, messageModifier: prompt, checkpointSaver: memory })
// highlight-end
```


```typescript
await agent2.invoke({ messages: [{ role: "user", content: "I'm Nemo!" }]}, { configurable: { thread_id: "1" } })
```
```output
{
  messages: [
    HumanMessage {
      "id": "a4a4f663-8192-4179-afcc-88d9d186aa80",
      "content": "I'm Nemo!",
      "additional_kwargs": {},
      "response_metadata": {}
    },
    AIMessage {
      "id": "chatcmpl-ABTKi4tBzOWMh3hgA46xXo7bJzb8r",
      "content": "How can I assist you today?",
      "additional_kwargs": {},
      "response_metadata": {
        "tokenUsage": {
          "completionTokens": 8,
          "promptTokens": 93,
          "totalTokens": 101
        },
        "finish_reason": "stop",
        "system_fingerprint": "fp_e375328146"
      },
      "tool_calls": [],
      "invalid_tool_calls": [],
      "usage_metadata": {
        "input_tokens": 93,
        "output_tokens": 8,
        "total_tokens": 101
      }
    }
  ]
}
```
And then if we rerun our wrapped agent executor:


```typescript
await agent2.invoke({ messages: [{ role: "user", content: "What is my name?" }]}, { configurable: { thread_id: "1" } })
```
```output
{
  messages: [
    HumanMessage {
      "id": "c5fd303c-eb49-41a0-868e-bc8c5aa02cf6",
      "content": "I'm Nemo!",
      "additional_kwargs": {},
      "response_metadata": {}
    },
    AIMessage {
      "id": "chatcmpl-ABTKi4tBzOWMh3hgA46xXo7bJzb8r",
      "content": "How can I assist you today?",
      "additional_kwargs": {},
      "response_metadata": {
        "tokenUsage": {
          "completionTokens": 8,
          "promptTokens": 93,
          "totalTokens": 101
        },
        "finish_reason": "stop",
        "system_fingerprint": "fp_e375328146"
      },
      "tool_calls": [],
      "invalid_tool_calls": []
    },
    HumanMessage {
      "id": "635b17b9-2ec7-412f-bf45-85d0e9944430",
      "content": "What is my name?",
      "additional_kwargs": {},
      "response_metadata": {}
    },
    AIMessage {
      "id": "chatcmpl-ABTKjBbmFlPb5t37aJ8p4NtoHb8YG",
      "content": "How can I assist you today?",
      "additional_kwargs": {},
      "response_metadata": {
        "tokenUsage": {
          "completionTokens": 8,
          "promptTokens": 93,
          "totalTokens": 101
        },
        "finish_reason": "stop",
        "system_fingerprint": "fp_e375328146"
      },
      "tool_calls": [],
      "invalid_tool_calls": [],
      "usage_metadata": {
        "input_tokens": 93,
        "output_tokens": 8,
        "total_tokens": 101
      }
    }
  ]
}
```
This [LangSmith trace](https://smith.langchain.com/public/16cbcfa5-5ef1-4d4c-92c9-538a6e71f23d/r) shows what's going on under the hood.

## Further reading

For more on how to build agents, check these [LangGraph](https://langchain-ai.github.io/langgraphjs/) guides:

* [agents conceptual guide](https://langchain-ai.github.io/langgraphjs/concepts/agentic_concepts/)
* [agents tutorials](https://langchain-ai.github.io/langgraphjs/tutorials/multi_agent/multi_agent_collaboration/)
* [createReactAgent](https://langchain-ai.github.io/langgraphjs/how-tos/create-react-agent/)

For more on tool usage, you can also check out [this use case section](/docs/how_to#tools).
