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
  model: "google-genai:gemini-3.5-flash",
  tools: [fetchUserData],
  contextSchema,
});

// :remove-start:
const directResult = await fetchUserData.invoke(
  { query: "recent activity" },
  { context: { userId: "user-123", apiKey: "sk-test" } },
);
if (!directResult.includes("user-123")) {
  throw new Error(`unexpected tool output: ${directResult}`);
}
if (!agent) {
  throw new Error("agent not created");
}

console.log("✓ context-engineering-runtime-context sample validated");
process.exit(0);
// :remove-end:
const result = await agent.invoke(
  { messages: [{ role: "user", content: "Get my recent activity" }] },
  { context: { userId: "user-123", apiKey: "sk-..." } },
);
// :snippet-end:
