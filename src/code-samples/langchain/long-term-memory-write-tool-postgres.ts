// :snippet-start: long-term-memory-write-tool-postgres-js
import * as z from "zod";
import { tool, createAgent, type ToolRuntime } from "langchain";
import { PostgresStore } from "@langchain/langgraph-checkpoint-postgres/store";

const DB_URI =
  process.env.POSTGRES_URI ??
  "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable";
const store = PostgresStore.fromConnString(DB_URI);
// :remove-start:
// Drop tables from prior runs (Python samples use different schema; CI shares one DB)
await (
  store as { core: { pool: { query: (q: string) => Promise<unknown> } } }
).core.pool.query(
  "DROP TABLE IF EXISTS public.store_vectors CASCADE; DROP TABLE IF EXISTS public.store CASCADE; DROP TABLE IF EXISTS public.store_migrations CASCADE;",
);
// :remove-end:
await store.setup();

const contextSchema = z.object({ userId: z.string() });

const UserInfo = z.object({ name: z.string() });

const saveUserInfo = tool(
  async (
    userInfo: z.infer<typeof UserInfo>,
    runtime: ToolRuntime<unknown, z.infer<typeof contextSchema>>,
  ) => {
    const userId = runtime.context.userId;
    if (!userId) throw new Error("userId is required");
    await runtime.store.put(["users"], userId, userInfo);
    return "Successfully saved user info.";
  },
  { name: "save_user_info", description: "Save user info", schema: UserInfo },
);

const agent = createAgent({
  model: "claude-sonnet-4-6",
  tools: [saveUserInfo],
  contextSchema,
  store,
});

await agent.invoke(
  { messages: [{ role: "user", content: "My name is John Smith" }] },
  { context: { userId: "user_123" } },
);

const result = await store.get(["users"], "user_123");
console.log(result?.value);
// :snippet-end:

// :remove-start:
async function main() {
  const DB_URI =
    process.env.POSTGRES_URI ||
    "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable";
  const store = PostgresStore.fromConnString(DB_URI);

  try {
    await store.setup();

    const contextSchema = z.object({ userId: z.string() });
    const UserInfo = z.object({ name: z.string() });

    const saveUserInfo = tool(
      async (
        userInfo: z.infer<typeof UserInfo>,
        runtime: ToolRuntime<unknown, z.infer<typeof contextSchema>>,
      ) => {
        const userId = runtime.context.userId;
        if (!userId) throw new Error("userId is required");
        await runtime.store.put(["users"], userId, userInfo);
        return "Successfully saved user info.";
      },
      {
        name: "save_user_info",
        description: "Save user info",
        schema: UserInfo,
      },
    );

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

    console.log("✓ Write tool with PostgresStore works correctly");
  } finally {
    await store.stop();
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
// :remove-end:
