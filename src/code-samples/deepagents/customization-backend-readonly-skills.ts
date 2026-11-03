// :snippet-start: backend-readonly-skills-js
import { InMemoryStore } from "@langchain/langgraph";
import {
  createDeepAgent,
  CompositeBackend,
  StateBackend,
  StoreBackend,
} from "deepagents";

const store = new InMemoryStore(); // Good for local dev; omit for LangSmith Deployment

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  backend: new CompositeBackend(new StateBackend(), {
    "/skills/": new StoreBackend({
      namespace: (rt) => ["curated-skills", rt.context.orgId],
    }),
  }),
  skills: ["/skills/"],
  permissions: [
    {
      operations: ["write"],
      paths: ["/skills/**"],
      mode: "deny",
    },
  ],
  store,
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
// :remove-end:
