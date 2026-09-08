// :snippet-start: long-term-memory-write-tool-inmemory-js
import * as z from "zod";
import { tool, createAgent, type ToolRuntime } from "langchain";
import { InMemoryStore } from "@langchain/langgraph";

// InMemoryStore saves data to an in-memory dictionary. Use a DB-backed store in production.
const store = new InMemoryStore();

const contextSchema = z.object({
  userId: z.string(),
});

// Schema defines the structure of user information for the LLM
const UserInfo = z.object({
  name: z.string(),
});

// Tool that allows agent to update user information (useful for chat applications)
const saveUserInfo = tool(
  async (
    userInfo: z.infer<typeof UserInfo>,
    runtime: ToolRuntime<unknown, z.infer<typeof contextSchema>>,
  ) => {
    const userId = runtime.context.userId;
    if (!userId) {
      throw new Error("userId is required");
    }
    // Store data in the store (namespace, key, data)
    await runtime.store.put(["users"], userId, userInfo);
    return "Successfully saved user info.";
  },
  {
    name: "save_user_info",
    description: "Save user info",
    schema: UserInfo,
  },
);

const agent = createAgent({
  model: "claude-sonnet-4-6",
  tools: [saveUserInfo],
  contextSchema,
  store,
});

// Run the agent
await agent.invoke(
  { messages: [{ role: "user", content: "My name is John Smith" }] },
  // userId passed in context to identify whose information is being updated
  { context: { userId: "user_123" } },
);

// You can access the store directly to get the value
const result = await store.get(["users"], "user_123");
console.log(result?.value); // Output: { name: "John Smith" }
// :snippet-end:

// :remove-start:
async function main() {
  // Test the tool directly - pass context and store in config (same shape as ToolRuntime)
  const saveResult = await saveUserInfo.invoke(
    { name: "John Smith" },
    { context: { userId: "user_123" }, store },
  );

  if (saveResult !== "Successfully saved user info.") {
    throw new Error("Expected save to succeed");
  }

  // Verify data was saved
  const savedData = await store.get(["users"], "user_123");
  if (!savedData) {
    throw new Error("Expected data to be saved");
  }
  if (savedData.value["name"] !== "John Smith") {
    throw new Error('Expected name to be "John Smith"');
  }

  console.log("✓ Write tool with InMemoryStore works correctly");
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
// :remove-end:
