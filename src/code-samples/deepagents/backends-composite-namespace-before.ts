// :snippet-start: backends-composite-namespace-before-js
import { createDeepAgent, CompositeBackend, StateBackend, StoreBackend } from "deepagents";

const agent = createDeepAgent({
  backend: (config) => new CompositeBackend(
    new StateBackend(config),
    { "/memories/": new StoreBackend(config, {
      namespace: ({ config: cfg }) => [
        String(cfg?.configurable?.langgraph_auth_user_id),
      ],
    }) },
  ),
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("expected agent");
console.log("✓ backends-composite-namespace-before validated");
// :remove-end:
