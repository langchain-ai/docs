// :remove-start:
process.env.ANTHROPIC_API_KEY ??= "sk-ant-test-key";
// :remove-end:
// :snippet-start: langgraph-quickstart-graph-js
import { ChatAnthropic } from "@langchain/anthropic";
import { tool } from "@langchain/core/tools";
import {
  StateGraph,
  StateSchema,
  MessagesValue,
  ReducedValue,
  GraphNode,
  ConditionalEdgeRouter,
  START,
  END,
} from "@langchain/langgraph";
import { SystemMessage, AIMessage, ToolMessage, HumanMessage } from "@langchain/core/messages";
import * as z from "zod";
// :remove-start:
const fakeArithmeticModel = {
  bindTools() {
    return this;
  },
  async invoke(messages: Array<{ type?: string }>) {
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

// Step 3: Define state

const MessagesState = new StateSchema({
  messages: MessagesValue,
  llmCalls: new ReducedValue(
    z.number().default(0),
    { reducer: (x, y) => x + y }
  ),
});

// Step 4: Define model node

const llmCall: GraphNode<typeof MessagesState> = async (state) => {
  return {
    messages: [await modelWithTools.invoke([
      new SystemMessage(
        "You are a helpful assistant tasked with performing arithmetic on a set of inputs."
      ),
      ...state.messages,
    ])],
    llmCalls: 1,
  };
};

// Step 5: Define tool node

const toolNode: GraphNode<typeof MessagesState> = async (state) => {
  const lastMessage = state.messages.at(-1);

  if (lastMessage == null || !AIMessage.isInstance(lastMessage)) {
    return { messages: [] };
  }

  const result: ToolMessage[] = [];
  for (const toolCall of lastMessage.tool_calls ?? []) {
    const tool = toolsByName[toolCall.name];
    const observation = await tool.invoke(toolCall);
    result.push(observation);
  }

  return { messages: result };
};

// Step 6: Define end logic

const shouldContinue: ConditionalEdgeRouter<{ InputSchema: typeof MessagesState; Nodes: "toolNode" }> = (state) => {
  const lastMessage = state.messages.at(-1);

  // Check if it's an AIMessage before accessing tool_calls
  if (!lastMessage || !AIMessage.isInstance(lastMessage)) {
    return END;
  }

  // If the LLM makes a tool call, then perform an action
  if (lastMessage.tool_calls?.length) {
    return "toolNode";
  }

  // Otherwise, we stop (reply to the user)
  return END;
};

// Step 7: Build and compile the agent

const agent = new StateGraph(MessagesState)
  .addNode("llmCall", llmCall)
  .addNode("toolNode", toolNode)
  .addEdge(START, "llmCall")
  .addConditionalEdges("llmCall", shouldContinue, ["toolNode", END])
  .addEdge("toolNode", "llmCall")
  .compile();

// Step 8: Set up LangSmith tracing (optional)
// export LANGSMITH_TRACING=true
// export LANGSMITH_API_KEY="your-langsmith-api-key"

// Step 9: Run the agent
const result = await agent.invoke({
  messages: [new HumanMessage("Add 3 and 4.")],
});

for (const message of result.messages) {
  console.log(`[${message.type}]: ${message.text}`);
}
// :snippet-end:

// :remove-start:
const toolResult = result.messages.find((message) => ToolMessage.isInstance(message));
if (toolResult == null || !String(toolResult.text).includes("7")) {
  throw new Error(`expected tool result 7, got ${JSON.stringify(result.messages)}`);
}
console.log("✓ langgraph-quickstart-graph");
// :remove-end:
