---
sidebar_position: 4
---

# How to create a custom chat model class

```{=mdx}
<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:

- [Chat models](/oss/concepts/chat_models)

</Info>
```
This notebook goes over how to create a custom chat model wrapper, in case you want to use your own chat model or a different wrapper than one that is directly supported in LangChain.

There are a few required things that a chat model needs to implement after extending the [`SimpleChatModel` class](https://api.js.langchain.com/classes/langchain_core.language_models_chat_models.SimpleChatModel.html):

- A `_call` method that takes in a list of messages and call options (which includes things like `stop` sequences), and returns a string.
- A `_llmType` method that returns a string. Used for logging purposes only.

You can also implement the following optional method:

- A `_streamResponseChunks` method that returns an `AsyncGenerator` and yields [`ChatGenerationChunks`](https://api.js.langchain.com/classes/langchain_core.outputs.ChatGenerationChunk.html). This allows the LLM to support streaming outputs.

Let's implement a very simple custom chat model that just echoes back the first `n` characters of the input.


```typescript
import {
  SimpleChatModel,
  type BaseChatModelParams,
} from "@langchain/core/language_models/chat_models";
import { CallbackManagerForLLMRun } from "@langchain/core/callbacks/manager";
import { AIMessageChunk, type BaseMessage } from "@langchain/core/messages";
import { ChatGenerationChunk } from "@langchain/core/outputs";

interface CustomChatModelInput extends BaseChatModelParams {
  n: number;
}

class CustomChatModel extends SimpleChatModel {
  n: number;

  constructor(fields: CustomChatModelInput) {
    super(fields);
    this.n = fields.n;
  }

  _llmType() {
    return "custom";
  }

  async _call(
    messages: BaseMessage[],
    options: this["ParsedCallOptions"],
    runManager?: CallbackManagerForLLMRun
  ): Promise<string> {
    if (!messages.length) {
      throw new Error("No messages provided.");
    }
    // Pass `runManager?.getChild()` when invoking internal runnables to enable tracing
    // await subRunnable.invoke(params, runManager?.getChild());
    if (typeof messages[0].content !== "string") {
      throw new Error("Multimodal messages are not supported.");
    }
    return messages[0].content.slice(0, this.n);
  }

  async *_streamResponseChunks(
    messages: BaseMessage[],
    options: this["ParsedCallOptions"],
    runManager?: CallbackManagerForLLMRun
  ): AsyncGenerator<ChatGenerationChunk> {
    if (!messages.length) {
      throw new Error("No messages provided.");
    }
    if (typeof messages[0].content !== "string") {
      throw new Error("Multimodal messages are not supported.");
    }
    // Pass `runManager?.getChild()` when invoking internal runnables to enable tracing
    // await subRunnable.invoke(params, runManager?.getChild());
    for (const letter of messages[0].content.slice(0, this.n)) {
      yield new ChatGenerationChunk({
        message: new AIMessageChunk({
          content: letter,
        }),
        text: letter,
      });
      // Trigger the appropriate callback for new chunks
      await runManager?.handleLLMNewToken(letter);
    }
  }
}
```
We can now use this as any other chat model:


```typescript
const chatModel = new CustomChatModel({ n: 4 });

await chatModel.invoke([["human", "I am an LLM"]]);
```
```output
AIMessage {
  lc_serializable: true,
  lc_kwargs: {
    content: 'I am',
    tool_calls: [],
    invalid_tool_calls: [],
    additional_kwargs: {},
    response_metadata: {}
  },
  lc_namespace: [ 'langchain_core', 'messages' ],
  content: 'I am',
  name: undefined,
  additional_kwargs: {},
  response_metadata: {},
  id: undefined,
  tool_calls: [],
  invalid_tool_calls: [],
  usage_metadata: undefined
}
```
And support streaming:


```typescript
const stream = await chatModel.stream([["human", "I am an LLM"]]);

for await (const chunk of stream) {
  console.log(chunk);
}
```
```output
AIMessageChunk {
  lc_serializable: true,
  lc_kwargs: {
    content: 'I',
    tool_calls: [],
    invalid_tool_calls: [],
    tool_call_chunks: [],
    additional_kwargs: {},
    response_metadata: {}
  },
  lc_namespace: [ 'langchain_core', 'messages' ],
  content: 'I',
  name: undefined,
  additional_kwargs: {},
  response_metadata: {},
  id: undefined,
  tool_calls: [],
  invalid_tool_calls: [],
  tool_call_chunks: [],
  usage_metadata: undefined
}
AIMessageChunk {
  lc_serializable: true,
  lc_kwargs: {
    content: ' ',
    tool_calls: [],
    invalid_tool_calls: [],
    tool_call_chunks: [],
    additional_kwargs: {},
    response_metadata: {}
  },
  lc_namespace: [ 'langchain_core', 'messages' ],
  content: ' ',
  name: undefined,
  additional_kwargs: {},
  response_metadata: {},
  id: undefined,
  tool_calls: [],
  invalid_tool_calls: [],
  tool_call_chunks: [],
  usage_metadata: undefined
}
AIMessageChunk {
  lc_serializable: true,
  lc_kwargs: {
    content: 'a',
    tool_calls: [],
    invalid_tool_calls: [],
    tool_call_chunks: [],
    additional_kwargs: {},
    response_metadata: {}
  },
  lc_namespace: [ 'langchain_core', 'messages' ],
  content: 'a',
  name: undefined,
  additional_kwargs: {},
  response_metadata: {},
  id: undefined,
  tool_calls: [],
  invalid_tool_calls: [],
  tool_call_chunks: [],
  usage_metadata: undefined
}
AIMessageChunk {
  lc_serializable: true,
  lc_kwargs: {
    content: 'm',
    tool_calls: [],
    invalid_tool_calls: [],
    tool_call_chunks: [],
    additional_kwargs: {},
    response_metadata: {}
  },
  lc_namespace: [ 'langchain_core', 'messages' ],
  content: 'm',
  name: undefined,
  additional_kwargs: {},
  response_metadata: {},
  id: undefined,
  tool_calls: [],
  invalid_tool_calls: [],
  tool_call_chunks: [],
  usage_metadata: undefined
}
```
## Richer outputs

If you want to take advantage of LangChain's callback system for functionality like token tracking, you can extend the [`BaseChatModel`](https://api.js.langchain.com/classes/langchain_core.language_models_chat_models.BaseChatModel.html) class and implement the lower level
`_generate` method. It also takes a list of `BaseMessage`s as input, but requires you to construct and return a `ChatGeneration` object that permits additional metadata.
Here's an example:


```typescript
import { AIMessage, BaseMessage } from "@langchain/core/messages";
import { ChatResult } from "@langchain/core/outputs";
import {
  BaseChatModel,
  BaseChatModelCallOptions,
  BaseChatModelParams,
} from "@langchain/core/language_models/chat_models";
import { CallbackManagerForLLMRun } from "@langchain/core/callbacks/manager";

interface AdvancedCustomChatModelOptions
  extends BaseChatModelCallOptions {}

interface AdvancedCustomChatModelParams extends BaseChatModelParams {
  n: number;
}

class AdvancedCustomChatModel extends BaseChatModel<AdvancedCustomChatModelOptions> {
  n: number;

  static lc_name(): string {
    return "AdvancedCustomChatModel";
  }

  constructor(fields: AdvancedCustomChatModelParams) {
    super(fields);
    this.n = fields.n;
  }

  async _generate(
    messages: BaseMessage[],
    options: this["ParsedCallOptions"],
    runManager?: CallbackManagerForLLMRun
  ): Promise<ChatResult> {
    if (!messages.length) {
      throw new Error("No messages provided.");
    }
    if (typeof messages[0].content !== "string") {
      throw new Error("Multimodal messages are not supported.");
    }
    // Pass `runManager?.getChild()` when invoking internal runnables to enable tracing
    // await subRunnable.invoke(params, runManager?.getChild());
    const content = messages[0].content.slice(0, this.n);
    const tokenUsage = {
      usedTokens: this.n,
    };
    return {
      generations: [{ message: new AIMessage({ content }), text: content }],
      llmOutput: { tokenUsage },
    };
  }

  _llmType(): string {
    return "advanced_custom_chat_model";
  }
}
```

This will pass the additional returned information in callback events and in the `streamEvents method:


```typescript
const chatModel = new AdvancedCustomChatModel({ n: 4 });

const eventStream = await chatModel.streamEvents([["human", "I am an LLM"]], {
  version: "v2",
});

for await (const event of eventStream) {
  if (event.event === "on_chat_model_end") {
    console.log(JSON.stringify(event, null, 2));
  }
}
```
```output
{
  "event": "on_chat_model_end",
  "data": {
    "output": {
      "lc": 1,
      "type": "constructor",
      "id": [
        "langchain_core",
        "messages",
        "AIMessage"
      ],
      "kwargs": {
        "content": "I am",
        "tool_calls": [],
        "invalid_tool_calls": [],
        "additional_kwargs": {},
        "response_metadata": {
          "tokenUsage": {
            "usedTokens": 4
          }
        }
      }
    }
  },
  "run_id": "11dbdef6-1b91-407e-a497-1a1ce2974788",
  "name": "AdvancedCustomChatModel",
  "tags": [],
  "metadata": {
    "ls_model_type": "chat"
  }
}
```
## Tracing (advanced)

If you are implementing a custom chat model and want to use it with a tracing service like [LangSmith](https://smith.langchain.com/),
you can automatically log params used for a given invocation by implementing the `invocationParams()` method on the model.

This method is purely optional, but anything it returns will be logged as metadata for the trace.

Here's one pattern you might use:


```typescript
import { CallbackManagerForLLMRun } from "@langchain/core/callbacks/manager";
import { BaseChatModel, type BaseChatModelCallOptions, type BaseChatModelParams } from "@langchain/core/language_models/chat_models";
import { BaseMessage } from "@langchain/core/messages";
import { ChatResult } from "@langchain/core/outputs";

interface CustomChatModelOptions extends BaseChatModelCallOptions {
  // Some required or optional inner args
  tools: Record<string, any>[];
}

interface CustomChatModelParams extends BaseChatModelParams {
  temperature: number;
  n: number;
}

class CustomChatModel extends BaseChatModel<CustomChatModelOptions> {
  temperature: number;

  n: number;

  static lc_name(): string {
    return "CustomChatModel";
  }

  constructor(fields: CustomChatModelParams) {
    super(fields);
    this.temperature = fields.temperature;
    this.n = fields.n;
  }

  // Anything returned in this method will be logged as metadata in the trace.
  // It is common to pass it any options used to invoke the function.
  invocationParams(options?: this["ParsedCallOptions"]) {
    return {
      tools: options?.tools,
      n: this.n,
    };
  }

  async _generate(
    messages: BaseMessage[],
    options: this["ParsedCallOptions"],
    runManager?: CallbackManagerForLLMRun
  ): Promise<ChatResult> {
    if (!messages.length) {
      throw new Error("No messages provided.");
    }
    if (typeof messages[0].content !== "string") {
      throw new Error("Multimodal messages are not supported.");
    }
    const additionalParams = this.invocationParams(options);
    const content = await someAPIRequest(messages, additionalParams);
    return {
      generations: [{ message: new AIMessage({ content }), text: content }],
      llmOutput: {},
    };
  }

  _llmType(): string {
    return "advanced_custom_chat_model";
  }
}
```
