---
sidebar_position: 3
---

# How to add ad-hoc tool calling capability to LLMs and Chat Models

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:

- [LangChain Expression Language (LCEL)](/oss/concepts/lcel)
- [Chaining runnables](/oss/how-to/sequence/)
- [Tool calling](/oss/how-to/tool_calling/)

</Info>

In this guide we'll build a Chain that does not rely on any special model APIs (like tool calling, which we showed in the [Quickstart](/oss/how-to/tool_calling)) and instead just prompts the model directly to invoke tools.

## Setup

We'll need to install the following packages:

```{=mdx}
<Npm2Yarn>
  @langchain/core zod
</Npm2Yarn>
```
#### Set environment variables

```
# Optional, use LangSmith for best-in-class observability
LANGSMITH_API_KEY=your-api-key
LANGSMITH_TRACING=true

# Reduce tracing latency if you are not in a serverless environment
# LANGCHAIN_CALLBACKS_BACKGROUND=true
```
## Create a tool

First, we need to create a tool to call. For this example, we will create a custom tool from a function. For more information on all details related to creating custom tools, please see [this guide](/oss/how-to/custom_tools).


```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const multiplyTool = tool((input) => {
    return (input.first_int * input.second_int).toString()
}, {
    name: "multiply",
    description: "Multiply two integers together.",
    schema: z.object({
        first_int: z.number(),
        second_int: z.number(),
    })
})

```
```typescript
console.log(multiplyTool.name)
console.log(multiplyTool.description)
```
```output
multiply
Multiply two integers together.
```

```typescript
await multiplyTool.invoke({ first_int: 4, second_int: 5 })
```
```output
20
```
## Creating our prompt

We'll want to write a prompt that specifies the tools the model has access to, the arguments to those tools, and the desired output format of the model. In this case we'll instruct it to output a JSON blob of the form `{"name": "...", "arguments": {...}}`.

```{=mdx}
<Tip>
As of `langchain` version `0.2.8`, the `renderTextDescription` function now supports [OpenAI-formatted tools](https://api.js.langchain.com/interfaces/langchain_core.language_models_base.ToolDefinition.html).
</Tip>
```
```typescript
import { renderTextDescription } from "langchain/tools/render";

const renderedTools = renderTextDescription([multiplyTool])
```


```typescript
import { ChatPromptTemplate } from "@langchain/core/prompts";

const systemPrompt = `You are an assistant that has access to the following set of tools. Here are the names and descriptions for each tool:

{rendered_tools}

Given the user input, return the name and input of the tool to use. Return your response as a JSON blob with 'name' and 'arguments' keys.`;

const prompt = ChatPromptTemplate.fromMessages(
    [["system", systemPrompt], ["user", "{input}"]]
)
```

## Adding an output parser

We'll use the `JsonOutputParser` for parsing our models output to JSON.

```{=mdx}
<ChatModelTabs />
```
```typescript
import { JsonOutputParser } from "@langchain/core/output_parsers";
const chain = prompt.pipe(model).pipe(new JsonOutputParser())
await chain.invoke({ input: "what's thirteen times 4", rendered_tools: renderedTools })
```
```output
{ name: 'multiply', arguments: [ 13, 4 ] }
```
## Invoking the tool

We can invoke the tool as part of the chain by passing along the model-generated "arguments" to it:


```typescript
import { RunnableLambda, RunnablePick } from "@langchain/core/runnables"

const chain = prompt.pipe(model).pipe(new JsonOutputParser()).pipe(new RunnablePick("arguments")).pipe(new RunnableLambda({ func: (input) => multiplyTool.invoke({
  first_int: input[0],
  second_int: input[1]
}) }))
await chain.invoke({ input: "what's thirteen times 4", rendered_tools: renderedTools })
```
```output
52
```
## Choosing from multiple tools

Suppose we have multiple tools we want the chain to be able to choose from:


```typescript
const addTool = tool((input) => {
    return (input.first_int + input.second_int).toString()
}, {
    name: "add",
    description: "Add two integers together.",
    schema: z.object({
        first_int: z.number(),
        second_int: z.number(),
    }),
});

const exponentiateTool = tool((input) => {
    return Math.pow(input.first_int, input.second_int).toString()
}, {
    name: "exponentiate",
    description: "Exponentiate the base to the exponent power.",
    schema: z.object({
        first_int: z.number(),
        second_int: z.number(),
    }),
});


```

With function calling, we can do this like so:

If we want to run the model selected tool, we can do so using a function that returns the tool based on the model output. Specifically, our function will action return it's own subchain that gets the "arguments" part of the model output and passes it to the chosen tool:


```typescript
import { StructuredToolInterface } from "@langchain/core/tools"

const tools = [addTool, exponentiateTool, multiplyTool]

const toolChain = (modelOutput) => {
    const toolMap: Record<string, StructuredToolInterface> = Object.fromEntries(tools.map(tool => [tool.name, tool]))
    const chosenTool = toolMap[modelOutput.name]
    return new RunnablePick("arguments").pipe(new RunnableLambda({ func: (input) => chosenTool.invoke({
        first_int: input[0],
        second_int: input[1]
      }) }))
}
const toolChainRunnable = new RunnableLambda({
  func: toolChain
})

const renderedTools = renderTextDescription(tools)
const systemPrompt = `You are an assistant that has access to the following set of tools. Here are the names and descriptions for each tool:

{rendered_tools}

Given the user input, return the name and input of the tool to use. Return your response as a JSON blob with 'name' and 'arguments' keys.`

const prompt = ChatPromptTemplate.fromMessages(
    [["system", systemPrompt], ["user", "{input}"]]
)
const chain = prompt.pipe(model).pipe(new JsonOutputParser()).pipe(toolChainRunnable)
await chain.invoke({ input: "what's 3 plus 1132", rendered_tools: renderedTools })
```
```output
1135
```
## Returning tool inputs

It can be helpful to return not only tool outputs but also tool inputs. We can easily do this with LCEL by `RunnablePassthrough.assign`-ing the tool output. This will take whatever the input is to the RunnablePassrthrough components (assumed to be a dictionary) and add a key to it while still passing through everything that's currently in the input:


```typescript
import { RunnablePassthrough } from "@langchain/core/runnables"

const chain = prompt.pipe(model).pipe(new JsonOutputParser()).pipe(RunnablePassthrough.assign({ output: toolChainRunnable }))
await chain.invoke({ input: "what's 3 plus 1132", rendered_tools: renderedTools })

```
```output
{ name: 'add', arguments: [ 3, 1132 ], output: '1135' }
```
## What's next?

This how-to guide shows the "happy path" when the model correctly outputs all the required tool information.

In reality, if you're using more complex tools, you will start encountering errors from the model, especially for models that have not been fine tuned for tool calling and for less capable models.

You will need to be prepared to add strategies to improve the output from the model; e.g.,

- Provide few shot examples.
- Add error handling (e.g., catch the exception and feed it back to the LLM to ask it to correct its previous output).
