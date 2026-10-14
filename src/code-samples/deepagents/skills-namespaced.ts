// :snippet-start: skills-namespaced-js
import {
  createDeepAgent,
  CompositeBackend,
  StateBackend,
  StoreBackend,
} from "deepagents";

// KEEP MODEL
const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  skills: ["/skills/"],
  backend: new CompositeBackend(new StateBackend(), {
    "/skills/": new StoreBackend({
      namespace: (ctx) => [
        ctx.assistantId ?? "default",
        ctx.config?.configurable?.user_id ?? "anonymous",
      ],
    }),
  }),
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ skills-namespaced sample validated");
// :remove-end:
