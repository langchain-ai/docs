// :snippet-start: long-term-memory-storage-postgres-js
import { PostgresStore } from "@langchain/langgraph-checkpoint-postgres/store";

const embed = (texts: string[]): number[][] => {
  return texts.map(() => [1.0, 2.0]);
};

const DB_URI =
  process.env.POSTGRES_URI ??
  "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable";
const store = PostgresStore.fromConnString(DB_URI, {
  index: { embed, dims: 2 },
});
// :remove-start:
// Drop tables from prior runs (Python samples use different schema; CI shares one DB)
await (
  store as { core: { pool: { query: (q: string) => Promise<unknown> } } }
).core.pool.query(
  "DROP TABLE IF EXISTS public.store_vectors CASCADE; DROP TABLE IF EXISTS public.store CASCADE; DROP TABLE IF EXISTS public.store_migrations CASCADE;",
);
// :remove-end:
await store.setup();

const userId = "my-user";
const applicationContext = "chitchat";
const namespace = [userId, applicationContext];

await store.put(namespace, "a-memory", {
  rules: [
    "User likes short, direct language",
    "User only speaks English & TypeScript",
  ],
  "my-key": "my-value",
});

const item = await store.get(namespace, "a-memory");
const items = await store.search(namespace, {
  filter: { "my-key": "my-value" },
  query: "language preferences",
});
// :snippet-end:

// :remove-start:

try {
  await store.setup();

  const userId = "my-user";
  const applicationContext = "chitchat";
  const namespace = [userId, applicationContext];

  await store.put(namespace, "a-memory", {
    rules: [
      "User likes short, direct language",
      "User only speaks English & TypeScript",
    ],
    "my-key": "my-value",
  });

  const item = await store.get(namespace, "a-memory");
  const items = await store.search(namespace, {
    filter: { "my-key": "my-value" },
    query: "language preferences",
  });

  // Verify the operations work
  if (!item) {
    throw new Error("Item should not be null");
  }
  if (item.value["my-key"] !== "my-value") {
    throw new Error('Expected my-key to be "my-value"');
  }
  if (!item.value["rules"]) {
    throw new Error("Expected rules to exist");
  }
  if ((item.value["rules"] as string[]).length !== 2) {
    throw new Error("Expected 2 rules");
  }

  // Verify search returns results
  if (items.length === 0) {
    throw new Error("Expected search to return results");
  }

  console.log("✓ PostgresStore operations work correctly");
} finally {
  await store.stop();
}

// :remove-end:
