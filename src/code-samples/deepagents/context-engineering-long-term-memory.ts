// :snippet-start: context-engineering-long-term-memory-js
import {
  CompositeBackend,
  createDeepAgent,
  StateBackend,
  StoreBackend,
} from "deepagents";
import { InMemoryStore } from "@langchain/langgraph-checkpoint";

const agent = await createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  store: new InMemoryStore(),
  backend: new CompositeBackend(new StateBackend(), {
    "/memories/": new StoreBackend(),
  }),
  systemPrompt: `When users tell you their preferences, save them to /memories/user_preferences.txt so you remember them in future conversations.`,
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ context-engineering-long-term-memory sample validated");
// :remove-end:
