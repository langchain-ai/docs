# How to filter messages

<Note>
The `filterMessages` function is available in `@langchain/core` version `0.2.8` and above.
</Note>

In more complex chains and agents we might track state with a list of messages. This list can start to accumulate messages from multiple different models, speakers, sub-chains, etc., and we may only want to pass subsets of this full list of messages to each model call in the chain/agent.

The `filterMessages` utility makes it easy to filter messages by type, id, or name.

## Basic usage


```typescript
import { HumanMessage, SystemMessage, AIMessage, filterMessages } from "@langchain/core/messages"

const messages = [
    new SystemMessage({ content: "you are a good assistant", id: "1" }),
    new HumanMessage({ content: "example input", id: "2", name: "example_user" }),
    new AIMessage({ content: "example output", id: "3", name: "example_assistant" }),
    new HumanMessage({ content: "real input", id: "4", name: "bob" }),
    new AIMessage({ content: "real output", id: "5", name: "alice" }),
]

filterMessages(messages, { includeTypes: ["human"] })
```
```output
[
  HumanMessage {
    lc_serializable: true,
    lc_kwargs: {
      content: 'example input',
      id: '2',
      name: 'example_user',
      additional_kwargs: {},
      response_metadata: {}
    },
    lc_namespace: [ 'langchain_core', 'messages' ],
    content: 'example input',
    name: 'example_user',
    additional_kwargs: {},
    response_metadata: {},
    id: '2'
  },
  HumanMessage {
    lc_serializable: true,
    lc_kwargs: {
      content: 'real input',
      id: '4',
      name: 'bob',
      additional_kwargs: {},
      response_metadata: {}
    },
    lc_namespace: [ 'langchain_core', 'messages' ],
    content: 'real input',
    name: 'bob',
    additional_kwargs: {},
    response_metadata: {},
    id: '4'
  }
]
```

```typescript
filterMessages(messages, { excludeNames: ["example_user", "example_assistant"] })
```
```output
[
  SystemMessage {
    lc_serializable: true,
    lc_kwargs: {
      content: 'you are a good assistant',
      id: '1',
      additional_kwargs: {},
      response_metadata: {}
    },
    lc_namespace: [ 'langchain_core', 'messages' ],
    content: 'you are a good assistant',
    name: undefined,
    additional_kwargs: {},
    response_metadata: {},
    id: '1'
  },
  HumanMessage {
    lc_serializable: true,
    lc_kwargs: {
      content: 'real input',
      id: '4',
      name: 'bob',
      additional_kwargs: {},
      response_metadata: {}
    },
    lc_namespace: [ 'langchain_core', 'messages' ],
    content: 'real input',
    name: 'bob',
    additional_kwargs: {},
    response_metadata: {},
    id: '4'
  },
  AIMessage {
    lc_serializable: true,
    lc_kwargs: {
      content: 'real output',
      id: '5',
      name: 'alice',
      tool_calls: [],
      invalid_tool_calls: [],
      additional_kwargs: {},
      response_metadata: {}
    },
    lc_namespace: [ 'langchain_core', 'messages' ],
    content: 'real output',
    name: 'alice',
    additional_kwargs: {},
    response_metadata: {},
    id: '5',
    tool_calls: [],
    invalid_tool_calls: [],
    usage_metadata: undefined
  }
]
```

```typescript
filterMessages(messages, { includeTypes: [HumanMessage, AIMessage], excludeIds: ["3"] })

```
```output
[
  HumanMessage {
    lc_serializable: true,
    lc_kwargs: {
      content: 'example input',
      id: '2',
      name: 'example_user',
      additional_kwargs: {},
      response_metadata: {}
    },
    lc_namespace: [ 'langchain_core', 'messages' ],
    content: 'example input',
    name: 'example_user',
    additional_kwargs: {},
    response_metadata: {},
    id: '2'
  },
  HumanMessage {
    lc_serializable: true,
    lc_kwargs: {
      content: 'real input',
      id: '4',
      name: 'bob',
      additional_kwargs: {},
      response_metadata: {}
    },
    lc_namespace: [ 'langchain_core', 'messages' ],
    content: 'real input',
    name: 'bob',
    additional_kwargs: {},
    response_metadata: {},
    id: '4'
  },
  AIMessage {
    lc_serializable: true,
    lc_kwargs: {
      content: 'real output',
      id: '5',
      name: 'alice',
      tool_calls: [],
      invalid_tool_calls: [],
      additional_kwargs: {},
      response_metadata: {}
    },
    lc_namespace: [ 'langchain_core', 'messages' ],
    content: 'real output',
    name: 'alice',
    additional_kwargs: {},
    response_metadata: {},
    id: '5',
    tool_calls: [],
    invalid_tool_calls: [],
    usage_metadata: undefined
  }
]
```
## Chaining

`filterMessages` can be used in an imperatively (like above) or declaratively, making it easy to compose with other components in a chain:


```typescript
import { ChatAnthropic } from "@langchain/anthropic";

const llm = new ChatAnthropic({ model: "claude-3-sonnet-20240229", temperature: 0 })
// Notice we don't pass in messages. This creates
// a RunnableLambda that takes messages as input
const filter_ = filterMessages({ excludeNames: ["example_user", "example_assistant"], end })
const chain = filter_.pipe(llm);
await chain.invoke(messages)
```
```output
AIMessage {
  lc_serializable: true,
  lc_kwargs: {
    content: [],
    additional_kwargs: {
      id: 'msg_01S2LQc1NLhtPHurW3jNRsCK',
      type: 'message',
      role: 'assistant',
      model: 'claude-3-sonnet-20240229',
      stop_reason: 'end_turn',
      stop_sequence: null,
      usage: [Object]
    },
    tool_calls: [],
    usage_metadata: { input_tokens: 16, output_tokens: 3, total_tokens: 19 },
    invalid_tool_calls: [],
    response_metadata: {}
  },
  lc_namespace: [ 'langchain_core', 'messages' ],
  content: [],
  name: undefined,
  additional_kwargs: {
    id: 'msg_01S2LQc1NLhtPHurW3jNRsCK',
    type: 'message',
    role: 'assistant',
    model: 'claude-3-sonnet-20240229',
    stop_reason: 'end_turn',
    stop_sequence: null,
    usage: { input_tokens: 16, output_tokens: 3 }
  },
  response_metadata: {
    id: 'msg_01S2LQc1NLhtPHurW3jNRsCK',
    model: 'claude-3-sonnet-20240229',
    stop_reason: 'end_turn',
    stop_sequence: null,
    usage: { input_tokens: 16, output_tokens: 3 }
  },
  id: undefined,
  tool_calls: [],
  invalid_tool_calls: [],
  usage_metadata: { input_tokens: 16, output_tokens: 3, total_tokens: 19 }
}
```
Looking at [the LangSmith trace](https://smith.langchain.com/public/a48c7935-04a8-4e87-9893-b14064ddbfc4/r) we can see that before the messages are passed to the model they are filtered.

Looking at just the filter_, we can see that it's a Runnable object that can be invoked like all Runnables:


```typescript
await filter_.invoke(messages)
```
```output
[
  SystemMessage {
    lc_serializable: true,
    lc_kwargs: {
      content: 'you are a good assistant',
      id: '1',
      additional_kwargs: {},
      response_metadata: {}
    },
    lc_namespace: [ 'langchain_core', 'messages' ],
    content: 'you are a good assistant',
    name: undefined,
    additional_kwargs: {},
    response_metadata: {},
    id: '1'
  },
  HumanMessage {
    lc_serializable: true,
    lc_kwargs: {
      content: 'real input',
      id: '4',
      name: 'bob',
      additional_kwargs: {},
      response_metadata: {}
    },
    lc_namespace: [ 'langchain_core', 'messages' ],
    content: 'real input',
    name: 'bob',
    additional_kwargs: {},
    response_metadata: {},
    id: '4'
  },
  AIMessage {
    lc_serializable: true,
    lc_kwargs: {
      content: 'real output',
      id: '5',
      name: 'alice',
      tool_calls: [],
      invalid_tool_calls: [],
      additional_kwargs: {},
      response_metadata: {}
    },
    lc_namespace: [ 'langchain_core', 'messages' ],
    content: 'real output',
    name: 'alice',
    additional_kwargs: {},
    response_metadata: {},
    id: '5',
    tool_calls: [],
    invalid_tool_calls: [],
    usage_metadata: undefined
  }
]
```
## API reference

For a complete description of all arguments head to the [API reference](https://api.js.langchain.com/functions/langchain_core.messages.filterMessages.html).
