# How to add message history

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:

- [Chaining runnables](/oss/how-to/sequence/)
- [Prompt templates](/oss/concepts/prompt_templates)
- [Chat Messages](/oss/concepts/messages)

</Info>

```{=mdx}
<Note>
**This guide previously covered the [RunnableWithMessageHistory](https://api.js.langchain.com/classes/_langchain_core.runnables.RunnableWithMessageHistory.html) abstraction. You can access this version of the guide in the [v0.2 docs](https://js.langchain.com/v0.2/docs/how_to/message_history/).**


The LangGraph implementation offers a number of advantages over `RunnableWithMessageHistory`, including the ability to persist arbitrary components of an application's state (instead of only messages).

</Note>
```
Passing conversation state into and out a chain is vital when building a chatbot. LangGraph implements a built-in persistence layer, allowing chain states to be automatically persisted in memory, or external backends such as SQLite, Postgres or Redis. Details can be found in the LangGraph persistence documentation.

In this guide we demonstrate how to add persistence to arbitrary LangChain runnables by wrapping them in a minimal LangGraph application. This lets us persist the message history and other elements of the chain's state, simplifying the development of multi-turn applications. It also supports multiple threads, enabling a single application to interact separately with multiple users.

## Setup

```{=mdx}
<Npm2Yarn>
  @langchain/core @langchain/langgraph
</Npm2Yarn>
```
Let’s also set up a chat model that we’ll use for the below examples.

```{=mdx}
<ChatModelTabs customVarName="llm" />
```
```typescript
// @lc-docs-hide-cell

import { ChatOpenAI } from "@langchain/openai";

const llm = new ChatOpenAI({
  model: "gpt-4o",
  temperature: 0,
});
```

## Example: message inputs

Adding memory to a [chat model](/oss/concepts/chat_models) provides a simple example. Chat models accept a list of messages as input and output a message. LangGraph includes a built-in `MessagesState` that we can use for this purpose.

Below, we:
1. Define the graph state to be a list of messages;
2. Add a single node to the graph that calls a chat model;
3. Compile the graph with an in-memory checkpointer to store messages between runs.

<Info>
**The output of a LangGraph application is its [state](https://langchain-ai.github.io/langgraphjs/concepts/low_level/).**


</Info>


```typescript
import { START, END, MessagesAnnotation, StateGraph, MemorySaver } from "@langchain/langgraph";

// Define the function that calls the model
const callModel = async (state: typeof MessagesAnnotation.State) => {
  const response = await llm.invoke(state.messages);
  // Update message history with response:
  return { messages: response };
};

// Define a new graph
const workflow = new StateGraph(MessagesAnnotation)
  // Define the (single) node in the graph
  .addNode("model", callModel)
  .addEdge(START, "model")
  .addEdge("model", END);

// Add memory
const memory = new MemorySaver();
const app = workflow.compile({ checkpointer: memory });
```

When we run the application, we pass in a configuration object that specifies a `thread_id`. This ID is used to distinguish conversational threads (e.g., between different users).


```typescript
import { v4 as uuidv4 } from "uuid";

const config = { configurable: { thread_id: uuidv4() } }
```

We can then invoke the application:


```typescript
const input = [
  {
    role: "user",
    content: "Hi! I'm Bob.",
  }
]
const output = await app.invoke({ messages: input }, config)
// The output contains all messages in the state.
// This will log the last message in the conversation.
console.log(output.messages[output.messages.length - 1]);
```
```output
AIMessage {
  "id": "chatcmpl-ABTqCeKnMQmG9IH8dNF5vPjsgXtcM",
  "content": "Hi Bob! How can I assist you today?",
  "additional_kwargs": {},
  "response_metadata": {
    "tokenUsage": {
      "completionTokens": 10,
      "promptTokens": 12,
      "totalTokens": 22
    },
    "finish_reason": "stop",
    "system_fingerprint": "fp_e375328146"
  },
  "tool_calls": [],
  "invalid_tool_calls": [],
  "usage_metadata": {
    "input_tokens": 12,
    "output_tokens": 10,
    "total_tokens": 22
  }
}
```

```typescript
const input2 = [
  {
    role: "user",
    content: "What's my name?",
  }
]
const output2 = await app.invoke({ messages: input2 }, config)
console.log(output2.messages[output2.messages.length - 1]);
```
```output
AIMessage {
  "id": "chatcmpl-ABTqD5jrJXeKCpvoIDp47fvgw2OPn",
  "content": "Your name is Bob. How can I help you today, Bob?",
  "additional_kwargs": {},
  "response_metadata": {
    "tokenUsage": {
      "completionTokens": 14,
      "promptTokens": 34,
      "totalTokens": 48
    },
    "finish_reason": "stop",
    "system_fingerprint": "fp_e375328146"
  },
  "tool_calls": [],
  "invalid_tool_calls": [],
  "usage_metadata": {
    "input_tokens": 34,
    "output_tokens": 14,
    "total_tokens": 48
  }
}
```
Note that states are separated for different threads. If we issue the same query to a thread with a new `thread_id`, the model indicates that it does not know the answer:


```typescript
const config2 = { configurable: { thread_id: uuidv4() } }
const input3 = [
  {
    role: "user",
    content: "What's my name?",
  }
]
const output3 = await app.invoke({ messages: input3 }, config2)
console.log(output3.messages[output3.messages.length - 1]);
```
```output
AIMessage {
  "id": "chatcmpl-ABTqDkctxwmXjeGOZpK6Km8jdCqdl",
  "content": "I'm sorry, but I don't have access to personal information about users. How can I assist you today?",
  "additional_kwargs": {},
  "response_metadata": {
    "tokenUsage": {
      "completionTokens": 21,
      "promptTokens": 11,
      "totalTokens": 32
    },
    "finish_reason": "stop",
    "system_fingerprint": "fp_52a7f40b0b"
  },
  "tool_calls": [],
  "invalid_tool_calls": [],
  "usage_metadata": {
    "input_tokens": 11,
    "output_tokens": 21,
    "total_tokens": 32
  }
}
```
## Example: object inputs

LangChain runnables often accept multiple inputs via separate keys in a single object argument. A common example is a prompt template with multiple parameters.

Whereas before our runnable was a chat model, here we chain together a prompt template and chat model.


```typescript
import { ChatPromptTemplate, MessagesPlaceholder } from "@langchain/core/prompts";

const prompt = ChatPromptTemplate.fromMessages([
  ["system", "Answer in {language}."],
  new MessagesPlaceholder("messages"),
])

const runnable = prompt.pipe(llm);
```

For this scenario, we define the graph state to include these parameters (in addition to the message history). We then define a single-node graph in the same way as before.

Note that in the below state:
- Updates to the `messages` list will append messages;
- Updates to the `language` string will overwrite the string.


```typescript
import { START, END, StateGraph, MemorySaver, MessagesAnnotation, Annotation } from "@langchain/langgraph";

// Define the State
// highlight-next-line
const GraphAnnotation = Annotation.Root({
  // highlight-next-line
  language: Annotation<string>(),
  // Spread `MessagesAnnotation` into the state to add the `messages` field.
  // highlight-next-line
  ...MessagesAnnotation.spec,
})


// Define the function that calls the model
const callModel2 = async (state: typeof GraphAnnotation.State) => {
  const response = await runnable.invoke(state);
  // Update message history with response:
  return { messages: [response] };
};

const workflow2 = new StateGraph(GraphAnnotation)
  .addNode("model", callModel2)
  .addEdge(START, "model")
  .addEdge("model", END);

const app2 = workflow2.compile({ checkpointer: new MemorySaver() });
```


```typescript
const config3 = { configurable: { thread_id: uuidv4() } }
const input4 = {
  messages: [
    {
      role: "user",
      content: "What's my name?",
    }
  ],
  language: "Spanish",
} 
const output4 = await app2.invoke(input4, config3)
console.log(output4.messages[output4.messages.length - 1]);
```
```output
AIMessage {
  "id": "chatcmpl-ABTqFnCASRB5UhZ7XAbbf5T0Bva4U",
  "content": "Lo siento, pero no tengo suficiente información para saber tu nombre. ¿Cómo te llamas?",
  "additional_kwargs": {},
  "response_metadata": {
    "tokenUsage": {
      "completionTokens": 19,
      "promptTokens": 19,
      "totalTokens": 38
    },
    "finish_reason": "stop",
    "system_fingerprint": "fp_e375328146"
  },
  "tool_calls": [],
  "invalid_tool_calls": [],
  "usage_metadata": {
    "input_tokens": 19,
    "output_tokens": 19,
    "total_tokens": 38
  }
}
```
## Managing message history

The message history (and other elements of the application state) can be accessed via `.getState`:


```typescript
const state = (await app2.getState(config3)).values

console.log(`Language: ${state.language}`);
console.log(state.messages)
```
```output
Language: Spanish
[
  HumanMessage {
    "content": "What's my name?",
    "additional_kwargs": {},
    "response_metadata": {}
  },
  AIMessage {
    "id": "chatcmpl-ABTqFnCASRB5UhZ7XAbbf5T0Bva4U",
    "content": "Lo siento, pero no tengo suficiente información para saber tu nombre. ¿Cómo te llamas?",
    "additional_kwargs": {},
    "response_metadata": {
      "tokenUsage": {
        "completionTokens": 19,
        "promptTokens": 19,
        "totalTokens": 38
      },
      "finish_reason": "stop",
      "system_fingerprint": "fp_e375328146"
    },
    "tool_calls": [],
    "invalid_tool_calls": []
  }
]
```
We can also update the state via `.updateState`. For example, we can manually append a new message:


```typescript
const _ = await app2.updateState(config3, { messages: [{ role: "user", content: "test" }]})
```


```typescript
const state2 = (await app2.getState(config3)).values

console.log(`Language: ${state2.language}`);
console.log(state2.messages)
```
```output
Language: Spanish
[
  HumanMessage {
    "content": "What's my name?",
    "additional_kwargs": {},
    "response_metadata": {}
  },
  AIMessage {
    "id": "chatcmpl-ABTqFnCASRB5UhZ7XAbbf5T0Bva4U",
    "content": "Lo siento, pero no tengo suficiente información para saber tu nombre. ¿Cómo te llamas?",
    "additional_kwargs": {},
    "response_metadata": {
      "tokenUsage": {
        "completionTokens": 19,
        "promptTokens": 19,
        "totalTokens": 38
      },
      "finish_reason": "stop",
      "system_fingerprint": "fp_e375328146"
    },
    "tool_calls": [],
    "invalid_tool_calls": []
  },
  HumanMessage {
    "content": "test",
    "additional_kwargs": {},
    "response_metadata": {}
  }
]
```
For details on managing state, including deleting messages, see the LangGraph documentation:

- [How to delete messages](https://langchain-ai.github.io/langgraphjs/how-tos/delete-messages/)
- [How to view and update past graph state](https://langchain-ai.github.io/langgraphjs/how-tos/time-travel/)
