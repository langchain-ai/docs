// :snippet-start: long-term-memory-read-tool-postgres-js
import * as z from "zod";
import { createAgent, tool, type ToolRuntime } from "langchain";
import { PostgresStore } from "@langchain/langgraph-checkpoint-postgres/store";

const DB_URI =
  process.env.POSTGRES_URI ??
  "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable";
const store = PostgresStore.fromConnString(DB_URI);
// :remove-start:
// Drop old store tables if they exist (prior version used different schema).
// setup() uses CREATE TABLE IF NOT EXISTS and does not migrate existing tables.
await (
  store as { core: { pool: { query: (q: string) => Promise<unknown> } } }
).core.pool.query(
  "DROP TABLE IF EXISTS public.store_vectors CASCADE; DROP TABLE IF EXISTS public.store CASCADE; DROP TABLE IF EXISTS public.store_migrations CASCADE;",
);
// :remove-end:
await store.setup();

const contextSchema = z.object({ userId: z.string() });

await store.put(["users"], "user_123", {
  name: "John Smith",
  language: "English",
});

const getUserInfo = tool(
  async (_, runtime: ToolRuntime<unknown, z.infer<typeof contextSchema>>) => {
    const userId = runtime.context.userId;
    if (!userId) throw new Error("userId is required");
    const userInfo = await runtime.store.get(["users"], userId);
    return userInfo?.value ? JSON.stringify(userInfo.value) : "Unknown user";
  },
  {
    name: "getUserInfo",
    description: "Look up user info by userId from the store.",
    schema: z.object({}),
  },
);

const agent = createAgent({
  model: "claude-sonnet-4-6",
  tools: [getUserInfo],
  contextSchema,
  store,
});

await agent.invoke(
  { messages: [{ role: "user", content: "look up user information" }] },
  { context: { userId: "user_123" } },
);
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

    await store.put(["users"], "user_123", {
      name: "John Smith",
      language: "English",
    });

    // Verify the store has the data
    const storedData = await store.get(["users"], "user_123");
    if (!storedData) {
      throw new Error("Expected data to be in store");
    }
    if (storedData.value["name"] !== "John Smith") {
      throw new Error('Expected name to be "John Smith"');
    }

    console.log("✓ Read tool with PostgresStore works correctly");
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
