// :snippet-start: skills-writable-js
import { InMemoryStore } from "@langchain/langgraph";
import {
  createDeepAgent,
  CompositeBackend,
  StateBackend,
  StoreBackend,
} from "deepagents";

const store = new InMemoryStore(); // Good for local dev; omit for LangSmith Deployment

// KEEP MODEL
const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  backend: new CompositeBackend(new StateBackend(), {
    "/skills/approved/": new StoreBackend({
      namespace: (rt) => ["approved-skills", rt.context.orgId],
    }),
    "/skills/editable/": new StoreBackend({
      namespace: (ctx) => [
        "editable-skills",
        ctx.config?.configurable?.user_id ?? "anonymous",
      ],
    }),
  }),
  skills: ["/skills/approved/", "/skills/editable/"],
  permissions: [
    {
      operations: ["write"],
      paths: ["/skills/approved/**"],
      mode: "deny",
    },
  ],
  store,
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ skills-writable sample validated");
// :remove-end:
