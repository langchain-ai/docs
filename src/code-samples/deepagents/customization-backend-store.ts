// :snippet-start: backend-store-js
import { createDeepAgent, StoreBackend } from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore(); // Good for local dev; omit for LangSmith Agent Server

const agent = createDeepAgent({
  model: "openai:gpt-6.1-sol",
  backend: new StoreBackend({
    namespace: ({ config }) => [
      String(config?.configurable?.langgraph_auth_user_id),
    ],
  }),
  store,
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
// :remove-end:
