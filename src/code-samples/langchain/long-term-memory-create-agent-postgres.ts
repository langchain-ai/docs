// :snippet-start: long-term-memory-create-agent-postgres-js
import { createAgent } from "langchain";
import { PostgresStore } from "@langchain/langgraph-checkpoint-postgres/store";

const DB_URI =
  process.env.POSTGRES_URI ??
  "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable";
const store = PostgresStore.fromConnString(DB_URI);
await store.setup();

const agent = createAgent({
  model: "claude-sonnet-4-6",
  tools: [],
  store,
});
// :snippet-end:

// :remove-start:
if (!agent) {
  throw new Error("Agent creation failed");
}
console.log("✓ Agent with PostgresStore created successfully");
await store.stop();
// :remove-end:
