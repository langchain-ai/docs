// :snippet-start: long-term-memory-create-agent-inmemory-js
import { createAgent } from "langchain";
import { InMemoryStore } from "@langchain/langgraph";

// InMemoryStore saves data to an in-memory dictionary. Use a DB-backed store in production use.
const store = new InMemoryStore();

const agent = createAgent({
  model: "claude-sonnet-4-6",
  tools: [],
  store,
});
// :snippet-end:

// :remove-start:
if (import.meta.url === `file://${process.argv[1]}`) {
  // Verify the agent was created successfully
  if (!agent) {
    throw new Error("Agent creation failed");
  }
  console.log("✓ Agent with InMemoryStore created successfully");
}
// :remove-end:
