// :remove-start:
process.env.ANTHROPIC_API_KEY ??= "sk-ant-test-key";
import {
  AIMessage,
  ToolMessage,
  type BaseMessage as HarnessBaseMessage,
} from "@langchain/core/messages";

const fakeArithmeticModel = {
  bindTools() {
    return this;
  },
  async invoke(messages: HarnessBaseMessage[]) {
    if (messages.some((message) => ToolMessage.isInstance(message))) {
      return new AIMessage("The sum is 7.");
    }
    return new AIMessage({
      content: "",
      tool_calls: [
        {
          name: "add",
          args: { a: 3, b: 4 },
          id: "call_add_1",
          type: "tool_call",
        },
      ],
    });
  },
};
// :remove-end:
// :snippet-start: langgraph-quickstart-functional-js
import { ChatAnthropic } from "@langchain/anthropic";
import { tool } from "@langchain/core/tools";
import {
  task,
  entrypoint,
  addMessages,
} from "@langchain/langgraph";
import {
  SystemMessage,
  HumanMessage,
  type BaseMessage,
} from "@langchain/core/messages";
import type { ToolCall } from "@langchain/core/messages/tool";
import * as z from "zod";

// Step 2: Define tools and model

// KEEP MODEL
let model = new ChatAnthropic({
  model: "claude-sonnet-4-6",
  temperature: 0,
});
// :remove-start:
model = fakeArithmeticModel as unknown as ChatAnthropic;
// :remove-end:

// Define tools
const add = tool(({ a, b }) => a + b, {
  name: "add",
  description: "Add two numbers",
  schema: z.object({
    a: z.number().describe("First number"),
    b: z.number().describe("Second number"),
  }),
});

const multiply = tool(({ a, b }) => a * b, {
  name: "multiply",
  description: "Multiply two numbers",
  schema: z.object({
    a: z.number().describe("First number"),
    b: z.number().describe("Second number"),
  }),
});

const divide = tool(({ a, b }) => a / b, {
  name: "divide",
  description: "Divide two numbers",
  schema: z.object({
    a: z.number().describe("First number"),
    b: z.number().describe("Second number"),
  }),
});

// Augment the LLM with tools
const toolsByName = {
  [add.name]: add,
  [multiply.name]: multiply,
  [divide.name]: divide,
};
const tools = Object.values(toolsByName);
const modelWithTools = model.bindTools(tools);

// Step 3: Define model task

const callLlm = task({ name: "callLlm" }, async (messages: BaseMessage[]) => {
  return modelWithTools.invoke([
    new SystemMessage(
      "You are a helpful assistant tasked with performing arithmetic on a set of inputs."
    ),
    ...messages,
  ]);
});

// Step 4: Define tool task

const callTool = task({ name: "callTool" }, async (toolCall: ToolCall) => {
  const tool = toolsByName[toolCall.name];
  return tool.invoke(toolCall);
});

// Step 5: Define agent

const agent = entrypoint({ name: "agent" }, async (messages: BaseMessage[]) => {
  let modelResponse = await callLlm(messages);

  while (true) {
    if (!modelResponse.tool_calls?.length) {
      break;
    }

    // Execute tools
    const toolResults = await Promise.all(
      modelResponse.tool_calls.map((toolCall) => callTool(toolCall))
    );
    messages = addMessages(messages, [modelResponse, ...toolResults]);
    modelResponse = await callLlm(messages);
  }

  return messages;
});

// Step 6: Set up LangSmith tracing (optional)
// export LANGSMITH_TRACING=true
// export LANGSMITH_API_KEY="your-langsmith-api-key"

// Step 7: Run the agent
const result = await agent.invoke([new HumanMessage("Add 3 and 4.")]);

for (const message of result) {
  console.log(`[${message.type}]: ${message.text}`);
}
// :snippet-end:

// :remove-start:
const toolResult = result.find((message) => ToolMessage.isInstance(message));
if (toolResult == null || !String(toolResult.text).includes("7")) {
  throw new Error(`expected tool result 7, got ${JSON.stringify(result)}`);
}
console.log("✓ langgraph-quickstart-functional");
// :remove-end:
