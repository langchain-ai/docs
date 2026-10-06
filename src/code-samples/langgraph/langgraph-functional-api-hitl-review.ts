// :snippet-start: langgraph-functional-api-hitl-review-helper-js
import { ToolMessage } from "@langchain/core/messages";
import { ToolCall } from "@langchain/core/messages/tool";
import { interrupt } from "@langchain/langgraph";

type ToolCallReview =
  | { action: "continue"; data?: undefined }
  | { action: "update"; data: ToolCall["args"] }
  | { action: "feedback"; data: string };

function reviewToolCall(toolCall: ToolCall): ToolCall | ToolMessage {
  // Review a tool call, returning a validated version
  const humanReview = interrupt({
    question: "Is this correct?",
    tool_call: toolCall,
  }) as ToolCallReview;

  if (humanReview.action === "continue") {
    return toolCall;
  }
  if (humanReview.action === "update") {
    return { ...toolCall, args: humanReview.data };
  }
  if (humanReview.action === "feedback") {
    return new ToolMessage({
      content: humanReview.data,
      name: toolCall.name,
      tool_call_id: toolCall.id,
    });
  }

  throw new Error("Unknown review action");
}
// :snippet-end:

// :snippet-start: langgraph-functional-api-hitl-review-agent-js
import {
  AIMessage,
  BaseMessage,
  HumanMessage,
} from "@langchain/core/messages";
import {
  Command,
  MemorySaver,
  addMessages,
  entrypoint,
  getPreviousState,
  task,
} from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const callModel = task("callModel", async (messages: BaseMessage[]) => {
  const last = messages[messages.length - 1];
  if (last instanceof ToolMessage) {
    return new AIMessage({ content: "Search complete." });
  }
  return new AIMessage({
    content: "",
    tool_calls: [
      {
        name: "search",
        args: { query: "weather" },
        id: "call_1",
        type: "tool_call",
      },
    ],
  });
});

const callTool = task("callTool", async (toolCall: ToolCall) => {
  return new ToolMessage({
    content: `result for ${JSON.stringify(toolCall.args)}`,
    name: toolCall.name,
    tool_call_id: toolCall.id,
  });
});

const agent = entrypoint(
  { checkpointer, name: "agent" },
  async (messages: BaseMessage[]): Promise<BaseMessage> => {
    const previous = getPreviousState<BaseMessage[]>();
    if (previous !== undefined) {
      messages = addMessages(previous, messages);
    }

    let modelResponse = await callModel(messages);
    while (true) {
      if (!modelResponse.tool_calls?.length) {
        break;
      }

      // Review tool calls
      const toolResults: ToolMessage[] = [];
      const toolCalls: ToolCall[] = [];
      const updatedToolCalls = [...modelResponse.tool_calls];

      for (let i = 0; i < modelResponse.tool_calls.length; i++) {
        const review = reviewToolCall(modelResponse.tool_calls[i]);
        if (review instanceof ToolMessage) {
          toolResults.push(review);
        } else {
          // is a validated tool call
          toolCalls.push(review);
          updatedToolCalls[i] = review;
        }
      }

      const toolCallsChanged = updatedToolCalls.some(
        (call, i) => call !== modelResponse.tool_calls?.[i]
      );
      if (toolCallsChanged) {
        modelResponse = new AIMessage({
          content: modelResponse.content,
          tool_calls: updatedToolCalls,
        });
      }

      // Execute remaining tool calls
      const remainingToolResults = await Promise.all(
        toolCalls.map((toolCall) => callTool(toolCall))
      );

      // Append to message list
      messages = addMessages(messages, [
        modelResponse,
        ...toolResults,
        ...remainingToolResults,
      ]);

      // Call model again
      modelResponse = await callModel(messages);
    }

    // Generate final response
    messages = addMessages(messages, modelResponse);
    return entrypoint.final({ value: modelResponse, save: messages });
  }
);

const config = { configurable: { thread_id: "2" } };

const stream = await agent.streamEvents(
  [new HumanMessage("What's the weather?")],
  { ...config, version: "v3" }
);
for await (const chunk of stream.values) {
  console.log(chunk);
}

const result = await agent.invoke(
  new Command({ resume: { action: "continue" } }),
  config
);
console.log(result);
// :snippet-end:

// :remove-start:
const text =
  typeof result.content === "string"
    ? result.content
    : JSON.stringify(result.content);
if (text !== "Search complete.") {
  throw new Error(`expected Search complete, got ${text}`);
}
console.log("✓ langgraph-functional-api-hitl-review");
// :remove-end:
