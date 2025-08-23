# How to chain runnables

One point about [LangChain Expression Language](/oss/concepts/lcel) is that any two runnables can be "chained" together into sequences. The output of the previous runnable's `.invoke()` call is passed as input to the next runnable. This can be done using the `.pipe()` method.

The resulting [`RunnableSequence`](https://api.js.langchain.com/classes/langchain_core.runnables.RunnableSequence.html) is itself a runnable, which means it can be invoked, streamed, or further chained just like any other runnable. Advantages of chaining runnables in this way are efficient streaming (the sequence will stream output as soon as it is available), and debugging and tracing with tools like [LangSmith](/oss/how-to/debugging).

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:

- [LangChain Expression Language (LCEL)](/oss/concepts/lcel)
- [Prompt templates](/oss/concepts/prompt_templates)
- [Chat models](/oss/concepts/chat_models)
- [Output parser](/oss/concepts/output_parsers)

</Info>

## The pipe method

To show off how this works, let's go through an example. We'll walk through a common pattern in LangChain: using a [prompt template](/oss/concepts/prompt_templates) to format input into a [chat model](/oss/concepts/chat_models), and finally converting the chat message output into a string with an [output parser](/oss/concepts/output_parsers).

```{=mdx}
<ChatModelTabs
  customVarName="model"
/>
```
```{=mdx}
import IntegrationInstallTooltip from "@mdx_components/integration_install_tooltip.mdx";
<IntegrationInstallTooltip></IntegrationInstallTooltip>

<Npm2Yarn>
  langchain @langchain/core
</Npm2Yarn>
```


```typescript
// @lc-docs-hide-cell
import { ChatOpenAI } from '@langchain/openai';

const model = new ChatOpenAI({
  model: "gpt-4o",
  temperature: 0,
})
```


```typescript
import { StringOutputParser } from "@langchain/core/output_parsers";
import { ChatPromptTemplate } from "@langchain/core/prompts";

const prompt = ChatPromptTemplate.fromTemplate("tell me a joke about {topic}")

const chain = prompt.pipe(model).pipe(new StringOutputParser())
```

Prompts and models are both runnable, and the output type from the prompt call is the same as the input type of the chat model, so we can chain them together. We can then invoke the resulting sequence like any other runnable:


```typescript
await chain.invoke({ topic: "bears" })
```



```output
"Here's a bear joke for you:\n\nWhy did the bear dissolve in water?\nBecause it was a polar bear!"
```


### Coercion

We can even combine this chain with more runnables to create another chain. This may involve some input/output formatting using other types of runnables, depending on the required inputs and outputs of the chain components.

For example, let's say we wanted to compose the joke generating chain with another chain that evaluates whether or not the generated joke was funny.

We would need to be careful with how we format the input into the next chain. In the below example, the dict in the chain is automatically parsed and converted into a [`RunnableParallel`](/oss/how-to/parallel), which runs all of its values in parallel and returns a dict with the results.

This happens to be the same format the next prompt template expects. Here it is in action:


```typescript
import { RunnableLambda } from "@langchain/core/runnables";

const analysisPrompt = ChatPromptTemplate.fromTemplate("is this a funny joke? {joke}")

const composedChain = new RunnableLambda({
  func: async (input: { topic: string }) => {
    const result = await chain.invoke(input);
    return { joke: result };
  }
}).pipe(analysisPrompt).pipe(model).pipe(new StringOutputParser())

await composedChain.invoke({ topic: "bears" })
```



```output
'Haha, that\'s a clever play on words! Using "polar" to imply the bear dissolved or became polar/polarized when put in water. Not the most hilarious joke ever, but it has a cute, groan-worthy pun that makes it mildly amusing. I appreciate a good pun or wordplay joke.'
```


Functions will also be coerced into runnables, so you can add custom logic to your chains too. The below chain results in the same logical flow as before:


```typescript
import { RunnableSequence } from "@langchain/core/runnables";

const composedChainWithLambda = RunnableSequence.from([
    chain,
    (input) => ({ joke: input }),
    analysisPrompt,
    model,
    new StringOutputParser()
])

await composedChainWithLambda.invoke({ topic: "beets" })
```



```output
"Haha, that's a cute and punny joke! I like how it plays on the idea of beets blushing or turning red like someone blushing. Food puns can be quite amusing. While not a total knee-slapper, it's a light-hearted, groan-worthy dad joke that would make me chuckle and shake my head. Simple vegetable humor!"
```


> See the LangSmith trace for the run above [here](https://smith.langchain.com/public/ef1bf347-a243-4da6-9be6-54f5d73e6da2/r)

However, keep in mind that using functions like this may interfere with operations like streaming. See [this section](/oss/how-to/functions) for more information.

## Next steps

You now know some ways to chain two runnables together.

To learn more, see the other how-to guides on runnables in [this section](/oss/how-to/#langchain-expression-language-lcel).
