# How to stream events from a tool

```{=mdx}
<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:
- [LangChain Tools](/oss/concepts/tools)
- [Custom tools](/oss/how-to/custom_tools)
- [Using stream events](/oss/how-to/streaming/#using-stream-events)
- [Accessing RunnableConfig within a custom tool](/oss/how-to/tool_configure/)

</Info>
```
If you have tools that call chat models, retrievers, or other runnables, you may want to access internal events from those runnables or configure them with additional properties. This guide shows you how to manually pass parameters properly so that you can do this using the [`.streamEvents()`](/oss/how-to/streaming/#using-stream-events) method.

```{=mdx}
<Warning>
**Compatibility**


In order to support a wider variety of JavaScript environments, the base LangChain package does not automatically propagate configuration to child runnables by default. This includes callbacks necessary for `.streamEvents()`. This is a common reason why you may fail to see events being emitted from custom runnables or tools.

You will need to manually propagate the `RunnableConfig` object to the child runnable. For an example of how to manually propagate the config, see the implementation of the `bar` RunnableLambda below.

This guide also requires `@langchain/core>=0.2.16`.
</Warning>
```
Say you have a custom tool that calls a chain that condenses its input by prompting a chat model to return only 10 words, then reversing the output. First, define it in a naive way:

```{=mdx}
<ChatModelTabs customVarName="model" />
```
```typescript
import { ChatAnthropic } from "@langchain/anthropic";
const model = new ChatAnthropic({
  model: "claude-3-5-sonnet-20240620",
  temperature: 0,
});
```


```typescript
import { z } from "zod";
import { tool } from "@langchain/core/tools";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";

const specialSummarizationTool = tool(async (input) => {
  const prompt = ChatPromptTemplate.fromTemplate(
    "You are an expert writer. Summarize the following text in 10 words or less:\n\n{long_text}"
  );
  const reverse = (x: string) => {
    return x.split("").reverse().join("");
  };
  const chain = prompt
    .pipe(model)
    .pipe(new StringOutputParser())
    .pipe(reverse);
  const summary = await chain.invoke({ long_text: input.long_text });
  return summary;
}, {
  name: "special_summarization_tool",
  description: "A tool that summarizes input text using advanced techniques.",
  schema: z.object({
    long_text: z.string(),
  }),
});
```

Invoking the tool directly works just fine:


```typescript
const LONG_TEXT = `
NARRATOR:
(Black screen with text; The sound of buzzing bees can be heard)
According to all known laws of aviation, there is no way a bee should be able to fly. Its wings are too small to get its fat little body off the ground. The bee, of course, flies anyway because bees don't care what humans think is impossible.
BARRY BENSON:
(Barry is picking out a shirt)
Yellow, black. Yellow, black. Yellow, black. Yellow, black. Ooh, black and yellow! Let's shake it up a little.
JANET BENSON:
Barry! Breakfast is ready!
BARRY:
Coming! Hang on a second.`;

await specialSummarizationTool.invoke({ long_text: LONG_TEXT });
```
```output
.yad noitaudarg rof tiftuo sesoohc yrraB ;scisyhp seifed eeB
```
But if you wanted to access the raw output from the chat model rather than the full tool, you might try to use the [`.streamEvents()`](/oss/how-to/streaming/#using-stream-events) method and look for an `on_chat_model_end` event. Here's what happens:


```typescript
const stream = await specialSummarizationTool.streamEvents(
  { long_text: LONG_TEXT },
  { version: "v2" },
);

for await (const event of stream) {
  if (event.event === "on_chat_model_end") {
    // Never triggers!
    console.log(event);
  }
}
```

You'll notice that there are no chat model events emitted from the child run!

This is because the example above does not pass the tool's config object into the internal chain. To fix this, redefine your tool to take a special parameter typed as `RunnableConfig` (see [this guide](/oss/how-to/tool_configure) for more details). You'll also need to pass that parameter through into the internal chain when executing it:


```typescript
const specialSummarizationToolWithConfig = tool(async (input, config) => {
  const prompt = ChatPromptTemplate.fromTemplate(
    "You are an expert writer. Summarize the following text in 10 words or less:\n\n{long_text}"
  );
  const reverse = (x: string) => {
    return x.split("").reverse().join("");
  };
  const chain = prompt
    .pipe(model)
    .pipe(new StringOutputParser())
    .pipe(reverse);
  // Pass the "config" object as an argument to any executed runnables
  const summary = await chain.invoke({ long_text: input.long_text }, config);
  return summary;
}, {
  name: "special_summarization_tool",
  description: "A tool that summarizes input text using advanced techniques.",
  schema: z.object({
    long_text: z.string(),
  }),
});
```

And now try the same `.streamEvents()` call as before with your new tool:


```typescript
const stream = await specialSummarizationToolWithConfig.streamEvents(
  { long_text: LONG_TEXT },
  { version: "v2" },
);

for await (const event of stream) {
  if (event.event === "on_chat_model_end") {
    // Never triggers!
    console.log(event);
  }
}
```
```output
{
  event: 'on_chat_model_end',
  data: {
    output: AIMessageChunk {
      lc_serializable: true,
      lc_kwargs: [Object],
      lc_namespace: [Array],
      content: 'Bee defies physics; Barry chooses outfit for graduation day.',
      name: undefined,
      additional_kwargs: [Object],
      response_metadata: {},
      id: undefined,
      tool_calls: [],
      invalid_tool_calls: [],
      tool_call_chunks: [],
      usage_metadata: [Object]
    },
    input: { messages: [Array] }
  },
  run_id: '27ac7b2e-591c-4adc-89ec-64d96e233ec8',
  name: 'ChatAnthropic',
  tags: [ 'seq:step:2' ],
  metadata: {
    ls_provider: 'anthropic',
    ls_model_name: 'claude-3-5-sonnet-20240620',
    ls_model_type: 'chat',
    ls_temperature: 0,
    ls_max_tokens: 2048,
    ls_stop: undefined
  }
}
```
Awesome! This time there's an event emitted.

For streaming, `.streamEvents()` automatically calls internal runnables in a chain with streaming enabled if possible, so if you wanted to a stream of tokens as they are generated from the chat model, you could simply filter to look for `on_chat_model_stream` events with no other changes:


```typescript
const stream = await specialSummarizationToolWithConfig.streamEvents(
  { long_text: LONG_TEXT },
  { version: "v2" },
);

for await (const event of stream) {
  if (event.event === "on_chat_model_stream") {
    // Never triggers!
    console.log(event);
  }
}
```
```output
{
  event: 'on_chat_model_stream',
  data: {
    chunk: AIMessageChunk {
      lc_serializable: true,
      lc_kwargs: [Object],
      lc_namespace: [Array],
      content: 'Bee',
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      id: undefined,
      tool_calls: [],
      invalid_tool_calls: [],
      tool_call_chunks: [],
      usage_metadata: undefined
    }
  },
  run_id: '938c0469-83c6-4dbd-862e-cd73381165de',
  name: 'ChatAnthropic',
  tags: [ 'seq:step:2' ],
  metadata: {
    ls_provider: 'anthropic',
    ls_model_name: 'claude-3-5-sonnet-20240620',
    ls_model_type: 'chat',
    ls_temperature: 0,
    ls_max_tokens: 2048,
    ls_stop: undefined
  }
}
{
  event: 'on_chat_model_stream',
  data: {
    chunk: AIMessageChunk {
      lc_serializable: true,
      lc_kwargs: [Object],
      lc_namespace: [Array],
      content: ' def',
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      id: undefined,
      tool_calls: [],
      invalid_tool_calls: [],
      tool_call_chunks: [],
      usage_metadata: undefined
    }
  },
  run_id: '938c0469-83c6-4dbd-862e-cd73381165de',
  name: 'ChatAnthropic',
  tags: [ 'seq:step:2' ],
  metadata: {
    ls_provider: 'anthropic',
    ls_model_name: 'claude-3-5-sonnet-20240620',
    ls_model_type: 'chat',
    ls_temperature: 0,
    ls_max_tokens: 2048,
    ls_stop: undefined
  }
}
{
  event: 'on_chat_model_stream',
  data: {
    chunk: AIMessageChunk {
      lc_serializable: true,
      lc_kwargs: [Object],
      lc_namespace: [Array],
      content: 'ies physics',
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      id: undefined,
      tool_calls: [],
      invalid_tool_calls: [],
      tool_call_chunks: [],
      usage_metadata: undefined
    }
  },
  run_id: '938c0469-83c6-4dbd-862e-cd73381165de',
  name: 'ChatAnthropic',
  tags: [ 'seq:step:2' ],
  metadata: {
    ls_provider: 'anthropic',
    ls_model_name: 'claude-3-5-sonnet-20240620',
    ls_model_type: 'chat',
    ls_temperature: 0,
    ls_max_tokens: 2048,
    ls_stop: undefined
  }
}
{
  event: 'on_chat_model_stream',
  data: {
    chunk: AIMessageChunk {
      lc_serializable: true,
      lc_kwargs: [Object],
      lc_namespace: [Array],
      content: ';',
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      id: undefined,
      tool_calls: [],
      invalid_tool_calls: [],
      tool_call_chunks: [],
      usage_metadata: undefined
    }
  },
  run_id: '938c0469-83c6-4dbd-862e-cd73381165de',
  name: 'ChatAnthropic',
  tags: [ 'seq:step:2' ],
  metadata: {
    ls_provider: 'anthropic',
    ls_model_name: 'claude-3-5-sonnet-20240620',
    ls_model_type: 'chat',
    ls_temperature: 0,
    ls_max_tokens: 2048,
    ls_stop: undefined
  }
}
{
  event: 'on_chat_model_stream',
  data: {
    chunk: AIMessageChunk {
      lc_serializable: true,
      lc_kwargs: [Object],
      lc_namespace: [Array],
      content: ' Barry',
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      id: undefined,
      tool_calls: [],
      invalid_tool_calls: [],
      tool_call_chunks: [],
      usage_metadata: undefined
    }
  },
  run_id: '938c0469-83c6-4dbd-862e-cd73381165de',
  name: 'ChatAnthropic',
  tags: [ 'seq:step:2' ],
  metadata: {
    ls_provider: 'anthropic',
    ls_model_name: 'claude-3-5-sonnet-20240620',
    ls_model_type: 'chat',
    ls_temperature: 0,
    ls_max_tokens: 2048,
    ls_stop: undefined
  }
}
{
  event: 'on_chat_model_stream',
  data: {
    chunk: AIMessageChunk {
      lc_serializable: true,
      lc_kwargs: [Object],
      lc_namespace: [Array],
      content: ' cho',
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      id: undefined,
      tool_calls: [],
      invalid_tool_calls: [],
      tool_call_chunks: [],
      usage_metadata: undefined
    }
  },
  run_id: '938c0469-83c6-4dbd-862e-cd73381165de',
  name: 'ChatAnthropic',
  tags: [ 'seq:step:2' ],
  metadata: {
    ls_provider: 'anthropic',
    ls_model_name: 'claude-3-5-sonnet-20240620',
    ls_model_type: 'chat',
    ls_temperature: 0,
    ls_max_tokens: 2048,
    ls_stop: undefined
  }
}
{
  event: 'on_chat_model_stream',
  data: {
    chunk: AIMessageChunk {
      lc_serializable: true,
      lc_kwargs: [Object],
      lc_namespace: [Array],
      content: 'oses outfit',
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      id: undefined,
      tool_calls: [],
      invalid_tool_calls: [],
      tool_call_chunks: [],
      usage_metadata: undefined
    }
  },
  run_id: '938c0469-83c6-4dbd-862e-cd73381165de',
  name: 'ChatAnthropic',
  tags: [ 'seq:step:2' ],
  metadata: {
    ls_provider: 'anthropic',
    ls_model_name: 'claude-3-5-sonnet-20240620',
    ls_model_type: 'chat',
    ls_temperature: 0,
    ls_max_tokens: 2048,
    ls_stop: undefined
  }
}
{
  event: 'on_chat_model_stream',
  data: {
    chunk: AIMessageChunk {
      lc_serializable: true,
      lc_kwargs: [Object],
      lc_namespace: [Array],
      content: ' for',
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      id: undefined,
      tool_calls: [],
      invalid_tool_calls: [],
      tool_call_chunks: [],
      usage_metadata: undefined
    }
  },
  run_id: '938c0469-83c6-4dbd-862e-cd73381165de',
  name: 'ChatAnthropic',
  tags: [ 'seq:step:2' ],
  metadata: {
    ls_provider: 'anthropic',
    ls_model_name: 'claude-3-5-sonnet-20240620',
    ls_model_type: 'chat',
    ls_temperature: 0,
    ls_max_tokens: 2048,
    ls_stop: undefined
  }
}
{
  event: 'on_chat_model_stream',
  data: {
    chunk: AIMessageChunk {
      lc_serializable: true,
      lc_kwargs: [Object],
      lc_namespace: [Array],
      content: ' graduation',
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      id: undefined,
      tool_calls: [],
      invalid_tool_calls: [],
      tool_call_chunks: [],
      usage_metadata: undefined
    }
  },
  run_id: '938c0469-83c6-4dbd-862e-cd73381165de',
  name: 'ChatAnthropic',
  tags: [ 'seq:step:2' ],
  metadata: {
    ls_provider: 'anthropic',
    ls_model_name: 'claude-3-5-sonnet-20240620',
    ls_model_type: 'chat',
    ls_temperature: 0,
    ls_max_tokens: 2048,
    ls_stop: undefined
  }
}
{
  event: 'on_chat_model_stream',
  data: {
    chunk: AIMessageChunk {
      lc_serializable: true,
      lc_kwargs: [Object],
      lc_namespace: [Array],
      content: ' day',
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      id: undefined,
      tool_calls: [],
      invalid_tool_calls: [],
      tool_call_chunks: [],
      usage_metadata: undefined
    }
  },
  run_id: '938c0469-83c6-4dbd-862e-cd73381165de',
  name: 'ChatAnthropic',
  tags: [ 'seq:step:2' ],
  metadata: {
    ls_provider: 'anthropic',
    ls_model_name: 'claude-3-5-sonnet-20240620',
    ls_model_type: 'chat',
    ls_temperature: 0,
    ls_max_tokens: 2048,
    ls_stop: undefined
  }
}
{
  event: 'on_chat_model_stream',
  data: {
    chunk: AIMessageChunk {
      lc_serializable: true,
      lc_kwargs: [Object],
      lc_namespace: [Array],
      content: '.',
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      id: undefined,
      tool_calls: [],
      invalid_tool_calls: [],
      tool_call_chunks: [],
      usage_metadata: undefined
    }
  },
  run_id: '938c0469-83c6-4dbd-862e-cd73381165de',
  name: 'ChatAnthropic',
  tags: [ 'seq:step:2' ],
  metadata: {
    ls_provider: 'anthropic',
    ls_model_name: 'claude-3-5-sonnet-20240620',
    ls_model_type: 'chat',
    ls_temperature: 0,
    ls_max_tokens: 2048,
    ls_stop: undefined
  }
}
```
## Automatically passing config (Advanced)

If you've used [LangGraph](https://langchain-ai.github.io/langgraphjs/), you may have noticed that you don't need to pass config in nested calls. This is because LangGraph takes advantage of an API called [`async_hooks`](https://nodejs.org/api/async_hooks.html), which is not supported in many, but not all environments.

If you wish, you can enable automatic configuration passing by running the following code to import and enable `AsyncLocalStorage` globally:


```typescript
import { AsyncLocalStorageProviderSingleton } from "@langchain/core/singletons";
import { AsyncLocalStorage } from "async_hooks";

AsyncLocalStorageProviderSingleton.initializeGlobalInstance(
  new AsyncLocalStorage()
);
```

## Next steps

You've now seen how to stream events from within a tool. Next, check out the following guides for more on using tools:

- Pass [runtime values to tools](/oss/how-to/tool_runtime)
- Pass [tool results back to a model](/oss/how-to/tool_results_pass_to_model)
- [Dispatch custom callback events](/oss/how-to/callbacks_custom_events)

You can also check out some more specific uses of tool calling:

- Building [tool-using chains and agents](/docs/how_to#tools)
- Getting [structured outputs](/oss/how-to/structured_output/) from models
