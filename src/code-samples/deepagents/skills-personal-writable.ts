// :snippet-start: skills-personal-writable-js
import {
  createDeepAgent,
  CompositeBackend,
  StateBackend,
  StoreBackend,
} from "deepagents";

// KEEP MODEL
const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  backend: new CompositeBackend(new StateBackend(), {
    "/skills/shared/": new StoreBackend({
      namespace: (rt) => ["curated-skills", rt.context.orgId],
    }),
    "/skills/personal/": new StoreBackend({
      namespace: (ctx) => [
        "user-skills",
        ctx.config?.configurable?.user_id ?? "anonymous",
      ],
    }),
  }),
  skills: ["/skills/shared/", "/skills/personal/"],
  permissions: [
    {
      operations: ["write"],
      paths: ["/skills/shared/**"],
      mode: "deny",
    },
  ],
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ skills-personal-writable sample validated");
// :remove-end:
