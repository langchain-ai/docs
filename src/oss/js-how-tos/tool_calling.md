# How to use chat models to call tools

```{=mdx}
<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:

- [Chat models](/oss/concepts/chat_models)
- [LangChain Tools](/oss/concepts/tools)
- [Tool calling](/oss/concepts/tool_calling)

</Info>
```
[Tool calling](/oss/concepts/tool_calling) allows a chat model to respond to a given prompt by "calling a tool".

Remember, while the name "tool calling" implies that the model is directly performing some action, this is actually not the case! The model only generates the arguments to a tool, and actually running the tool (or not) is up to the user.

Tool calling is a general technique that generates structured output from a model, and you can use it even when you don't intend to invoke any tools. An example use-case of that is [extraction from unstructured text](/oss/tutorials/extraction/).

![](../../static/img/tool_call.png)

If you want to see how to use the model-generated tool call to actually run a tool function [check out this guide](/oss/how-to/tool_results_pass_to_model/).

```{=mdx}
<Note>
**Supported models**


Tool calling is not universal, but is supported by many popular LLM providers, including [Anthropic](/oss/integrations/chat/anthropic/), 
[Cohere](/oss/integrations/chat/cohere/), [Google](/oss/integrations/chat/google_vertex_ai/), 
[Mistral](/oss/integrations/chat/mistral/), [OpenAI](/oss/integrations/chat/openai/), and even for locally-running models via [Ollama](/oss/integrations/chat/ollama/).

You can find a [list of all models that support tool calling here](/oss/integrations/chat/).

</Note>
```
LangChain implements standard interfaces for defining tools, passing them to LLMs, and representing tool calls.
This guide will cover how to bind tools to an LLM, then invoke the LLM to generate these arguments.

LangChain implements standard interfaces for defining tools, passing them to LLMs, 
and representing tool calls. This guide will show you how to use them.

## Passing tools to chat models

Chat models that support tool calling features implement a [`.bindTools()`](https://api.js.langchain.com/classes/langchain_core.language_models_chat_models.BaseChatModel.html#bindTools) method, which 
receives a list of LangChain [tool objects](https://api.js.langchain.com/classes/langchain_core.tools.StructuredTool.html)
and binds them to the chat model in its expected format. Subsequent invocations of the 
chat model will include tool schemas in its calls to the LLM.

```{=mdx}
<Note>
**As of `@langchain/core` version `0.2.9`, all chat models with tool calling capabilities now support [OpenAI-formatted tools](https://api.js.langchain.com/interfaces/langchain_core.language_models_base.ToolDefinition.html).**

:::
```
Let's walk through an example:

```{=mdx}
<ChatModelTabs customVarName="llm" providers={["anthropic", "openai", "mistral", "fireworks"]} additionalDependencies="@langchain/core" />
```
We can use the `.bindTools()` method to handle the conversion from LangChain tool to our model provider's specific format and bind it to the model (i.e., passing it in each time the model is invoked). A number of models implement helper methods that will take care of formatting and binding different function-like objects to the model.
Let's create a new tool implementing a Zod schema, then bind it to the model:

```{=mdx}
</Note>note
The `tool` function is available in `@langchain/core` version 0.2.7 and above.

If you are on an older version of core, you should use instantiate and use [`DynamicStructuredTool`](https://api.js.langchain.com/classes/langchain_core.tools.DynamicStructuredTool.html) instead.
:::
```
```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

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

Now, let's invoke it! We expect the model to use the calculator to answer the question:


```typescript
const res = await llmWithTools.invoke("What is 3 * 12");

console.log(res);
```
```output
AIMessage {
  "id": "chatcmpl-9p1Ib4xfxV4yahv2ZWm1IRb1fRVD7",
  "content": "",
  "additional_kwargs": {
    "tool_calls": [
      {
        "id": "call_CrZkMP0AvUrz7w9kim0splbl",
        "type": "function",
        "function": "[Object]"
      }
    ]
  },
  "response_metadata": {
    "tokenUsage": {
      "completionTokens": 24,
      "promptTokens": 93,
      "totalTokens": 117
    },
    "finish_reason": "tool_calls",
    "system_fingerprint": "fp_400f27fa1f"
  },
  "tool_calls": [
    {
      "name": "calculator",
      "args": {
        "operation": "multiply",
        "number1": 3,
        "number2": 12
      },
      "type": "tool_call",
      "id": "call_CrZkMP0AvUrz7w9kim0splbl"
    }
  ],
  "invalid_tool_calls": [],
  "usage_metadata": {
    "input_tokens": 93,
    "output_tokens": 24,
    "total_tokens": 117
  }
}
```
As we can see our LLM generated arguments to a tool!

**Note:** If you are finding that the model does not call a desired tool for a given prompt, you can see [this guide on how to force the LLM to call a tool](/oss/how-to/tool_choice/) rather than letting it decide.

```{=mdx}
<Tip>
See a LangSmith trace for the above [here](https://smith.langchain.com/public/b2222205-7da9-4a5a-8efe-6bc62347705d/r).
</Tip>
```
## Tool calls

If tool calls are included in a LLM response, they are attached to the corresponding 
[message](https://api.js.langchain.com/classes/langchain_core.messages.AIMessage.html) 
or [message chunk](https://api.js.langchain.com/classes/langchain_core.messages.AIMessageChunk.html) 
as a list of [tool call](https://api.js.langchain.com/types/langchain_core.messages_tool.ToolCall.html) 
objects in the `.tool_calls` attribute.

A `ToolCall` is a typed dict that includes a 
tool name, dict of argument values, and (optionally) an identifier. Messages with no 
tool calls default to an empty list for this attribute.

Chat models can call multiple tools at once. Here's an example:


```typescript
const res = await llmWithTools.invoke("What is 3 * 12? Also, what is 11 + 49?");

res.tool_calls;
```
```output
[
  {
    name: 'calculator',
    args: { operation: 'multiply', number1: 3, number2: 12 },
    type: 'tool_call',
    id: 'call_01lvdk2COLV2hTjRUNAX8XWH'
  },
  {
    name: 'calculator',
    args: { operation: 'add', number1: 11, number2: 49 },
    type: 'tool_call',
    id: 'call_fB0vo8VC2HRojZcj120xIBxM'
  }
]
```
The `.tool_calls` attribute should contain valid tool calls. Note that on occasion, 
model providers may output malformed tool calls (e.g., arguments that are not 
valid JSON). When parsing fails in these cases, instances 
of [`InvalidToolCall`](https://api.js.langchain.com/types/langchain_core.messages_tool.InvalidToolCall.html) 
are populated in the `.invalid_tool_calls` attribute. An `InvalidToolCall` can have 
a name, string arguments, identifier, and error message.

## Binding model-specific formats (advanced)

Providers adopt different conventions for formatting tool schemas. For instance, OpenAI uses a format like this:

- `type`: The type of the tool. At the time of writing, this is always "function".
- `function`: An object containing tool parameters.
- `function.name`: The name of the schema to output.
- `function.description`: A high level description of the schema to output.
- `function.parameters`: The nested details of the schema you want to extract, formatted as a [JSON schema](https://json-schema.org/) object.

We can bind this model-specific format directly to the model if needed. Here's an example:


```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4o" });

const modelWithTools = model.bind({
  tools: [{
    "type": "function",
    "function": {
      "name": "calculator",
      "description": "Can perform mathematical operations.",
      "parameters": {
        "type": "object",
        "properties": {
          "operation": {
            "type": "string",
            "description": "The type of operation to execute.",
            "enum": ["add", "subtract", "multiply", "divide"]
          },
          "number1": {"type": "number", "description": "First integer"},
          "number2": {"type": "number", "description": "Second integer"},
        },
        "required": ["number1", "number2"],
      },
    },
  }],
});

await modelWithTools.invoke(`Whats 119 times 8?`);
```
```output
AIMessage {
  "id": "chatcmpl-9p1IeP7mIp3jPn1wgsP92zxEfNo7k",
  "content": "",
  "additional_kwargs": {
    "tool_calls": [
      {
        "id": "call_P5Xgyi0Y7IfisaUmyapZYT7d",
        "type": "function",
        "function": "[Object]"
      }
    ]
  },
  "response_metadata": {
    "tokenUsage": {
      "completionTokens": 24,
      "promptTokens": 85,
      "totalTokens": 109
    },
    "finish_reason": "tool_calls",
    "system_fingerprint": "fp_400f27fa1f"
  },
  "tool_calls": [
    {
      "name": "calculator",
      "args": {
        "operation": "multiply",
        "number1": 119,
        "number2": 8
      },
      "type": "tool_call",
      "id": "call_P5Xgyi0Y7IfisaUmyapZYT7d"
    }
  ],
  "invalid_tool_calls": [],
  "usage_metadata": {
    "input_tokens": 85,
    "output_tokens": 24,
    "total_tokens": 109
  }
}
```
This is functionally equivalent to the `bind_tools()` calls above.

## Next steps

Now you've learned how to bind tool schemas to a chat model and have the model call the tool.

Next, check out this guide on actually using the tool by invoking the function and passing the results back to the model:

- Pass [tool results back to model](/oss/how-to/tool_results_pass_to_model)

You can also check out some more specific uses of tool calling:

- Few shot prompting [with tools](/oss/how-to/tools_few_shot/)
- Stream [tool calls](/oss/how-to/tool_streaming/)
- Pass [runtime values to tools](/oss/how-to/tool_runtime)
- Getting [structured outputs](/oss/how-to/structured_output/) from models
