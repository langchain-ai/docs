// :snippet-start: backend-composite-js
import {
  createDeepAgent,
  CompositeBackend,
  StateBackend,
  StoreBackend,
} from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();
// KEEP MODEL
const agent = createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  backend: new CompositeBackend(new StateBackend(), {
    "/memories/": new StoreBackend({
      namespace: () => ["memories"],
    }),
  }),
  store,
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
// :remove-end:
