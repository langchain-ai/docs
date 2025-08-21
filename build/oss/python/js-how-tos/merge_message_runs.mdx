# How to merge consecutive messages of the same type

<Note>
The `mergeMessageRuns` function is available in `@langchain/core` version `0.2.8` and above.
</Note>

Certain models do not support passing in consecutive messages of the same type (a.k.a. "runs" of the same message type).

The `mergeMessageRuns` utility makes it easy to merge consecutive messages of the same type.

## Basic usage


```typescript
import { HumanMessage, SystemMessage, AIMessage, mergeMessageRuns } from "@langchain/core/messages";

const messages = [
    new SystemMessage("you're a good assistant."),
    new SystemMessage("you always respond with a joke."),
    new HumanMessage({ content: [{"type": "text", "text": "i wonder why it's called langchain"}] }),
    new HumanMessage("and who is harrison chasing anyways"),
    new AIMessage(
        'Well, I guess they thought "WordRope" and "SentenceString" just didn\'t have the same ring to it!'
    ),
    new AIMessage("Why, he's probably chasing after the last cup of coffee in the office!"),
];

const merged = mergeMessageRuns(messages);
console.log(merged.map((x) => JSON.stringify({
    role: x._getType(),
    content: x.content,
}, null, 2)).join("\n\n"));
```
```output
{
  "role": "system",
  "content": "you're a good assistant.\nyou always respond with a joke."
}

{
  "role": "human",
  "content": [
    {
      "type": "text",
      "text": "i wonder why it's called langchain"
    },
    {
      "type": "text",
      "text": "and who is harrison chasing anyways"
    }
  ]
}

{
  "role": "ai",
  "content": "Well, I guess they thought \"WordRope\" and \"SentenceString\" just didn't have the same ring to it!\nWhy, he's probably chasing after the last cup of coffee in the office!"
}
```
Notice that if the contents of one of the messages to merge is a list of content blocks then the merged message will have a list of content blocks. And if both messages to merge have string contents then those are concatenated with a newline character.

## Chaining

`mergeMessageRuns` can be used in an imperatively (like above) or declaratively, making it easy to compose with other components in a chain:


```typescript
import { ChatAnthropic } from "@langchain/anthropic";
import { mergeMessageRuns } from "@langchain/core/messages";

const llm = new ChatAnthropic({ model: "claude-3-sonnet-20240229", temperature: 0 });
// Notice we don't pass in messages. This creates
// a RunnableLambda that takes messages as input
const merger = mergeMessageRuns();
const chain = merger.pipe(llm);
await chain.invoke(messages);
```
```output
AIMessage {
  lc_serializable: true,
  lc_kwargs: {
    content: [],
    additional_kwargs: {
      id: 'msg_01LsdS4bjQ3EznH7Tj4xujV1',
      type: 'message',
      role: 'assistant',
      model: 'claude-3-sonnet-20240229',
      stop_reason: 'end_turn',
      stop_sequence: null,
      usage: [Object]
    },
    tool_calls: [],
    usage_metadata: { input_tokens: 84, output_tokens: 3, total_tokens: 87 },
    invalid_tool_calls: [],
    response_metadata: {}
  },
  lc_namespace: [ 'langchain_core', 'messages' ],
  content: [],
  name: undefined,
  additional_kwargs: {
    id: 'msg_01LsdS4bjQ3EznH7Tj4xujV1',
    type: 'message',
    role: 'assistant',
    model: 'claude-3-sonnet-20240229',
    stop_reason: 'end_turn',
    stop_sequence: null,
    usage: { input_tokens: 84, output_tokens: 3 }
  },
  response_metadata: {
    id: 'msg_01LsdS4bjQ3EznH7Tj4xujV1',
    model: 'claude-3-sonnet-20240229',
    stop_reason: 'end_turn',
    stop_sequence: null,
    usage: { input_tokens: 84, output_tokens: 3 }
  },
  id: undefined,
  tool_calls: [],
  invalid_tool_calls: [],
  usage_metadata: { input_tokens: 84, output_tokens: 3, total_tokens: 87 }
}
```
Looking at [the LangSmith trace](https://smith.langchain.com/public/48d256fb-fd7e-48a0-bdfd-217ab74ad01d/r) we can see that before the messages are passed to the model they are merged.

Looking at just the merger, we can see that it's a Runnable object that can be invoked like all Runnables:


```typescript
await merger.invoke(messages)
```
```output
[
  SystemMessage {
    lc_serializable: true,
    lc_kwargs: {
      content: "you're a good assistant.\nyou always respond with a joke.",
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      id: undefined
    },
    lc_namespace: [ 'langchain_core', 'messages' ],
    content: "you're a good assistant.\nyou always respond with a joke.",
    name: undefined,
    additional_kwargs: {},
    response_metadata: {},
    id: undefined
  },
  HumanMessage {
    lc_serializable: true,
    lc_kwargs: {
      content: [Array],
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      id: undefined
    },
    lc_namespace: [ 'langchain_core', 'messages' ],
    content: [ [Object], [Object] ],
    name: undefined,
    additional_kwargs: {},
    response_metadata: {},
    id: undefined
  },
  AIMessage {
    lc_serializable: true,
    lc_kwargs: {
      content: `Well, I guess they thought "WordRope" and "SentenceString" just didn't have the same ring to it!\n` +
        "Why, he's probably chasing after the last cup of coffee in the office!",
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      id: undefined,
      tool_calls: [],
      invalid_tool_calls: [],
      usage_metadata: undefined
    },
    lc_namespace: [ 'langchain_core', 'messages' ],
    content: `Well, I guess they thought "WordRope" and "SentenceString" just didn't have the same ring to it!\n` +
      "Why, he's probably chasing after the last cup of coffee in the office!",
    name: undefined,
    additional_kwargs: {},
    response_metadata: {},
    id: undefined,
    tool_calls: [],
    invalid_tool_calls: [],
    usage_metadata: undefined
  }
]
```
## API reference

For a complete description of all arguments head to the [API reference](https://api.js.langchain.com/functions/langchain_core.messages.mergeMessageRuns.html).
