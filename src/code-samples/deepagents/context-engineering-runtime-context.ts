// :snippet-start: context-engineering-runtime-context-js
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import type { ToolRuntime } from "@langchain/core/tools";
import * as z from "zod";

const contextSchema = z.object({
  userId: z.string(),
  apiKey: z.string(),
});

const fetchUserData = tool(
  async (input, runtime: ToolRuntime<unknown, typeof contextSchema>) => {
    const userId = runtime.context?.userId;
    return `Data for user ${userId}: ${input.query}`;
  },
  {
    name: "fetch_user_data",
    description: "Fetch data for the current user",
    schema: z.object({ query: z.string() }),
  },
);

const agent = await createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  tools: [fetchUserData],
  contextSchema,
});

const result = await agent.invoke(
  { messages: [{ role: "user", content: "Get my recent activity" }] },
  { context: { userId: "user-123", apiKey: "sk-..." } },
);
// :snippet-end:

// :remove-start:
const directResult = await fetchUserData.invoke(
  { query: "recent activity" },
  { context: { userId: "user-123", apiKey: "sk-test" } },
);
if (!directResult.includes("user-123")) {
  throw new Error(`unexpected tool output: ${directResult}`);
}

const messages = result.messages ?? [];
const usedRuntimeContext = messages.some((message) => {
  const text =
    typeof message.content === "string"
      ? message.content
      : JSON.stringify(message.content);
  return text.includes("user-123");
});
if (!usedRuntimeContext) {
  throw new Error("expected agent response to use runtime context");
}

console.log("✓ context-engineering-runtime-context sample validated");
// :remove-end:
