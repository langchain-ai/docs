// :remove-start:
function getUserInfo(userId: string | undefined) {
  return { id: userId ?? null, name: "Test User" };
}
// :remove-end:

// :snippet-start: langgraph-graph-api-send-command-command-tool-js
import { tool } from "@langchain/core/tools";
import { Command } from "@langchain/langgraph";
import * as z from "zod";

const lookupUserInfo = tool(
  async (_input, runtime) => {
    const userId = runtime.serverInfo?.user?.identity as string | undefined;  // [!code highlight]
    const userInfo = getUserInfo(userId);
    return new Command({
      update: {
        userInfo,
        messages: [
          {
            role: "tool",
            content: "Successfully looked up user information",
            tool_call_id: runtime.toolCall.id,
          },
        ],
      },
    });
  },
  {
    name: "lookupUserInfo",
    description:
      "Look up user information to better assist with questions.",
    schema: z.object({}),
  }
);
// :snippet-end:

// :remove-start:
import { AIMessage } from "@langchain/core/messages";
import { MessagesValue, StateGraph, StateSchema, START } from "@langchain/langgraph";
import { ToolNode } from "@langchain/langgraph/prebuilt";

if (lookupUserInfo.name !== "lookupUserInfo") {
  throw new Error("Unexpected tool name");
}

const ToolState = new StateSchema({
  messages: MessagesValue,
  userInfo: z.record(z.string(), z.unknown()).optional(),
});

const toolGraph = new StateGraph(ToolState)
  .addNode("tools", new ToolNode([lookupUserInfo]))
  .addEdge(START, "tools")
  .compile();

const toolResult = await toolGraph.invoke({
  messages: [
    new AIMessage({
      content: "",
      tool_calls: [{ name: "lookupUserInfo", args: {}, id: "call_1" }],
    }),
  ],
});
if (toolResult.userInfo?.name !== "Test User") {
  throw new Error(`Unexpected userInfo: ${JSON.stringify(toolResult.userInfo)}`);
}
const lastMessage = toolResult.messages[toolResult.messages.length - 1];
if (
  lastMessage.content !== "Successfully looked up user information" ||
  (lastMessage as { tool_call_id?: string }).tool_call_id !== "call_1"
) {
  throw new Error(`Unexpected tool message: ${JSON.stringify(lastMessage)}`);
}
console.log("✓ langgraph-graph-api-send-command-command-tool-js");
// :remove-end:
