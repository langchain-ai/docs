// :snippet-start: backend-store-js
import { createDeepAgent, StoreBackend } from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore(); // Good for local dev; omit for LangSmith Deployment
// KEEP MODEL
const agent = createDeepAgent({
  model: "google_genai:gemini-3.1-pro-preview",
  backend: new StoreBackend({
    namespace: (ctx) => [ctx.runtime.context.userId],
  }),
  store,
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
// :remove-end:
