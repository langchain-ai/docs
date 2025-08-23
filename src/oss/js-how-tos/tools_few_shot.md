## How to use few-shot prompting with tool calling

```{=mdx}
<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:

- [Chat models](/oss/concepts/chat_models)
- [LangChain Tools](/oss/concepts/tools)
- [Tool calling](/oss/concepts/tool_calling)
- [Passing tool outputs to chat models](/oss/how-to/tool_results_pass_to_model/)

</Info>
```
For more complex tool use it's very useful to add few-shot examples to the prompt. We can do this by adding `AIMessages` with `ToolCalls` and corresponding `ToolMessages` to our prompt.

First define a model and a calculator tool:


```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { ChatOpenAI } from "@langchain/openai";

const llm = new ChatOpenAI({ model: "gpt-4o", temperature: 0, })

/**
 * Note that the descriptions here are crucial, as they will be passed along
 * to the model along with the class name.
 */
const calculatorSchema = z.object({
  operation: z
    .enum(["add", "subtract", "multiply", "divide"])
    .describe("The type of operation to execute."),
  number1: z.number().describe("The first number to operate on."),
  number2: z.number().describe("The second number to operate on."),
});

const calculatorTool = tool(async ({ operation, number1, number2 }) => {
  // Functions must return strings
  if (operation === "add") {
    return `${number1 + number2}`;
  } else if (operation === "subtract") {
    return `${number1 - number2}`;
  } else if (operation === "multiply") {
    return `${number1 * number2}`;
  } else if (operation === "divide") {
    return `${number1 / number2}`;
  } else {
    throw new Error("Invalid operation.");
  }
}, {
  name: "calculator",
  description: "Can perform mathematical operations.",
  schema: calculatorSchema,
});

const llmWithTools = llm.bindTools([calculatorTool]);
```
Our calculator can handle common addition, subtraction, multiplication, and division. But what happens if we ask about a new mathematical operator, `🦜`?

Let's see what happens when we use it naively:


```typescript
const res = await llmWithTools.invoke("What is 3 🦜 12");

console.log(res.content);
console.log(res.tool_calls);
```
```output

[
  {
    name: 'calculator',
    args: { operation: 'multiply', number1: 3, number2: 12 },
    type: 'tool_call',
    id: 'call_I0oQGmdESpIgcf91ej30p9aR'
  }
]
```
It doesn't quite know how to interpret `🦜` as an operation, and it defaults to `multiply`. Now, let's try giving it some examples in the form of a manufactured messages to steer it towards `divide`:


```typescript
import { HumanMessage, AIMessage, ToolMessage } from "@langchain/core/messages";

const res = await llmWithTools.invoke([
  new HumanMessage("What is 333382 🦜 1932?"),
  new AIMessage({
    content: "The 🦜 operator is shorthand for division, so we call the divide tool.",
    tool_calls: [{
      id: "12345",
      name: "calculator",
      args: {
        number1: 333382,
        number2: 1932,
        operation: "divide",
      }
    }]
  }),
  new ToolMessage({
    tool_call_id: "12345",
    content: "The answer is 172.558."
  }),
  new AIMessage("The answer is 172.558."),
  new HumanMessage("What is 6 🦜 2?"),
  new AIMessage({
    content: "The 🦜 operator is shorthand for division, so we call the divide tool.",
    tool_calls: [{
      id: "54321",
      name: "calculator",
      args: {
        number1: 6,
        number2: 2,
        operation: "divide",
      }
    }]
  }),
  new ToolMessage({
    tool_call_id: "54321",
    content: "The answer is 3."
  }),
  new AIMessage("The answer is 3."),
  new HumanMessage("What is 3 🦜 12?")
]);

console.log(res.tool_calls);
```
```output
[
  {
    name: 'calculator',
    args: { number1: 3, number2: 12, operation: 'divide' },
    type: 'tool_call',
    id: 'call_O6M4yDaA6s8oDqs2Zfl7TZAp'
  }
]
```
And we can see that it now equates `🦜` with the `divide` operation in the correct way!

## Related

- Stream [tool calls](/oss/how-to/tool_streaming/)
- Pass [runtime values to tools](/oss/how-to/tool_runtime)
- Getting [structured outputs](/oss/how-to/structured_output/) from models
