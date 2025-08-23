# How to handle tool errors

```{=mdx}
<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:
- [Chat models](/oss/concepts/chat_models)
- [LangChain Tools](/oss/concepts/tools)
- [How to use a model to call tools](/oss/how-to/tool_calling)

</Info>
```
Calling tools with an LLM isn't perfect. The model may try to call a tool that doesn't exist or fail to return arguments that match the requested schema. Strategies like keeping schemas simple, reducing the number of tools you pass at once, and having good names and descriptions can help mitigate this risk, but aren't foolproof.

This guide covers some ways to build error handling into your chains to mitigate these failure modes.

## Chain

Suppose we have the following (dummy) tool and tool-calling chain. We'll make our tool intentionally convoluted to try and trip up the model.


```typescript
import { z } from "zod";
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "@langchain/core/tools";

const llm = new ChatOpenAI({
  model: "gpt-3.5-turbo-0125",
  temperature: 0,
});

const complexTool = tool(async (params) => {
  return params.int_arg * params.float_arg;
}, {
  name: "complex_tool",
  description: "Do something complex with a complex tool.",
  schema: z.object({
    int_arg: z.number(),
    float_arg: z.number(),
    number_arg: z.object({}),
  })
});

const llmWithTools = llm.bindTools([complexTool]);

const chain = llmWithTools
  .pipe((message) => message.tool_calls?.[0].args)
  .pipe(complexTool);
```
We can see that when we try to invoke this chain the model fails to correctly call the tool:


```typescript
await chain.invoke(
  "use complex tool. the args are 5, 2.1, potato"
);
```
```output
Stack trace:
``````output
Error: Received tool input did not match expected schema
``````output
    at DynamicStructuredTool.call (file:///Users/jacoblee/Library/Caches/deno/npm/registry.npmjs.org/@langchain/core/0.2.16/dist/tools/index.js:100:19)
``````output
    at eventLoopTick (ext:core/01_core.js:63:7)
``````output
    at async RunnableSequence.invoke (file:///Users/jacoblee/Library/Caches/deno/npm/registry.npmjs.org/@langchain/core/0.2.16_1/dist/runnables/base.js:1139:27)
``````output
    at async <anonymous>:1:22
```

## Try/except tool call

The simplest way to more gracefully handle errors is to try/except the tool-calling step and return a helpful message on errors:


```typescript
const tryExceptToolWrapper = async (input, config) => {
  try {
    const result = await complexTool.invoke(input);
    return result;
  } catch (e) {
    return `Calling tool with arguments:\n\n${JSON.stringify(input)}\n\nraised the following error:\n\n${e}`
  }
}

const chainWithTools = llmWithTools
  .pipe((message) => message.tool_calls?.[0].args)
  .pipe(tryExceptToolWrapper);

const res = await chainWithTools.invoke("use complex tool. the args are 5, 2.1, potato");

console.log(res);
```
```output
Calling tool with arguments:

{"int_arg":5,"float_arg":2.1,"number_arg":"potato"}

raised the following error:

Error: Received tool input did not match expected schema
```
## Fallbacks

We can also try to fallback to a better model in the event of a tool invocation error. In this case we'll fall back to an identical chain that uses `gpt-4-1106-preview` instead of `gpt-3.5-turbo`.


```typescript
const badChain = llmWithTools
  .pipe((message) => message.tool_calls?.[0].args)
  .pipe(complexTool);

const betterModel = new ChatOpenAI({
  model: "gpt-4-1106-preview",
  temperature: 0,
}).bindTools([complexTool]);

const betterChain = betterModel
  .pipe((message) => message.tool_calls?.[0].args)
  .pipe(complexTool);

const chainWithFallback = badChain.withFallbacks([betterChain]);

await chainWithFallback.invoke("use complex tool. the args are 5, 2.1, potato");
```



```output
10.5
```


Looking at the [LangSmith trace](https://smith.langchain.com/public/ea31e7ca-4abc-48e3-9943-700100c86622/r) for this chain run, we can see that the first chain call fails as expected and it's the fallback that succeeds.

## Next steps

Now you've seen some strategies how to handle tool calling errors. Next, you can learn more about how to use tools:

- Few shot prompting [with tools](/oss/how-to/tool_calling#few-shotting-with-tools)
- Stream [tool calls](/oss/how-to/tool_streaming/)
- Pass [runtime values to tools](/oss/how-to/tool_runtime)

You can also check out some more specific uses of tool calling:

- Getting [structured outputs](/oss/how-to/structured_output/) from models
