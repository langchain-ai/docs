// :snippet-start: backend-composite-js
import {
  createDeepAgent,
  CompositeBackend,
  StateBackend,
  StoreBackend,
} from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
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
