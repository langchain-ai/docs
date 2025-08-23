# How to cancel execution

```{=mdx}
<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:

- [LangChain Expression Language](/oss/concepts/lcel)
- [Chains](/oss/how-to/sequence/)
- [Streaming](/oss/how-to/streaming/)

</Info>
```
When building longer-running chains or [LangGraph](https://langchain-ai.github.io/langgraphjs/) agents, you may want to interrupt execution in situations such as a user leaving your app or submitting a new query.

[LangChain Expression Language (LCEL)](/oss/concepts/lcel) supports aborting runnables that are in-progress via a runtime [signal](https://developer.mozilla.org/en-US/docs/Web/API/AbortController/signal) option.

```{=mdx}
<Warning>
**Compatibility**


Built-in signal support requires `@langchain/core>=0.2.20`. Please see here for a [guide on upgrading](/oss/how-to/installation/#installing-integration-packages).

</Warning>
```
**Note:** Individual integrations like chat models or retrievers may have missing or differing implementations for aborting execution. Signal support as described in this guide will apply in between steps of a chain.

To see how this works, construct a chain such as the one below that performs [retrieval-augmented generation](/oss/tutorials/rag). It answers questions by first searching the web using [Tavily](/oss/integrations/retrievers/tavily), then passing the results to a chat model to generate a final answer:

```{=mdx}
<ChatModelTabs />
```
```typescript
// @lc-docs-hide-cell
import { ChatAnthropic } from "@langchain/anthropic";

const llm = new ChatAnthropic({
  model: "claude-3-5-sonnet-20240620",
});
```


```typescript
import { TavilySearchAPIRetriever } from "@langchain/community/retrievers/tavily_search_api";
import type { Document } from "@langchain/core/documents";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { RunnablePassthrough, RunnableSequence } from "@langchain/core/runnables";

const formatDocsAsString = (docs: Document[]) => {
  return docs.map((doc) => doc.pageContent).join("\n\n")
}

const retriever = new TavilySearchAPIRetriever({
  k: 3,
});

const prompt = ChatPromptTemplate.fromTemplate(`
Use the following context to answer questions to the best of your ability:

<context>
{context}
</context>

Question: {question}`)

const chain = RunnableSequence.from([
  {
    context: retriever.pipe(formatDocsAsString),
    question: new RunnablePassthrough(),
  },
  prompt,
  llm,
  new StringOutputParser(),
]);
```

If you invoke it normally, you can see it returns up-to-date information:


```typescript
await chain.invoke("what is the current weather in SF?");
```
```output
Based on the provided context, the current weather in San Francisco is:

Temperature: 17.6°C (63.7°F)
Condition: Sunny
Wind: 14.4 km/h (8.9 mph) from WSW direction
Humidity: 74%
Cloud cover: 15%

The information indicates it's a sunny day with mild temperatures and light winds. The data appears to be from August 2, 2024, at 17:00 local time.
```
Now, let's interrupt it early. Initialize an [`AbortController`](https://developer.mozilla.org/en-US/docs/Web/API/AbortController) and pass its `signal` property into the chain execution. To illustrate the fact that the cancellation occurs as soon as possible, set a timeout of 100ms:


```typescript
const controller = new AbortController();

const startTimer = console.time("timer1");

setTimeout(() => controller.abort(), 100);

try {
  await chain.invoke("what is the current weather in SF?", {
    signal: controller.signal,
  });
} catch (e) {
  console.log(e);
}

console.timeEnd("timer1");
```
```output
Error: Aborted
    at EventTarget.<anonymous> (/Users/jacoblee/langchain/langchainjs/langchain-core/dist/utils/signal.cjs:19:24)
    at [nodejs.internal.kHybridDispatch] (node:internal/event_target:825:20)
    at EventTarget.dispatchEvent (node:internal/event_target:760:26)
    at abortSignal (node:internal/abort_controller:370:10)
    at AbortController.abort (node:internal/abort_controller:392:5)
    at Timeout._onTimeout (evalmachine.<anonymous>:7:29)
    at listOnTimeout (node:internal/timers:573:17)
    at process.processTimers (node:internal/timers:514:7)
timer1: 103.204ms
```
And you can see that execution ends after just over 100ms. Looking at [this LangSmith trace](https://smith.langchain.com/public/63c04c3b-2683-4b73-a4f7-fb12f5cb9180/r), you can see that the model is never called.

## Streaming

You can pass a `signal` when streaming too. This gives you more control over using a `break` statement within the `for await... of` loop to cancel the current run, which will only trigger after final output has already started streaming. The below example uses a `break` statement - note the time elapsed before cancellation occurs:


```typescript
const startTimer2 = console.time("timer2");

const stream = await chain.stream("what is the current weather in SF?");

for await (const chunk of stream) {
  console.log("chunk", chunk);
  break;
}

console.timeEnd("timer2");
```
```output
chunk 
timer2: 3.990s
```
Now compare this to using a signal. Note that you will need to wrap the stream in a `try/catch` block:


```typescript
const controllerForStream = new AbortController();

const startTimer3 = console.time("timer3");

setTimeout(() => controllerForStream.abort(), 100);

try {
  const streamWithSignal = await chain.stream("what is the current weather in SF?", {
    signal: controllerForStream.signal
  });
  for await (const chunk of streamWithSignal) {
    console.log(chunk);
    break;
  } 
} catch (e) {
  console.log(e);  
}

console.timeEnd("timer3");
```
```output
Error: Aborted
    at EventTarget.<anonymous> (/Users/jacoblee/langchain/langchainjs/langchain-core/dist/utils/signal.cjs:19:24)
    at [nodejs.internal.kHybridDispatch] (node:internal/event_target:825:20)
    at EventTarget.dispatchEvent (node:internal/event_target:760:26)
    at abortSignal (node:internal/abort_controller:370:10)
    at AbortController.abort (node:internal/abort_controller:392:5)
    at Timeout._onTimeout (evalmachine.<anonymous>:7:38)
    at listOnTimeout (node:internal/timers:573:17)
    at process.processTimers (node:internal/timers:514:7)
timer3: 100.684ms
```
## Related

- [Pass through arguments from one step to the next](/oss/how-to/passthrough)
- [Dispatching custom events](/oss/how-to/callbacks_custom_events)
