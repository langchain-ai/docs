// :snippet-start: backends-composite-namespace-after-js
import { createDeepAgent, CompositeBackend, StateBackend, StoreBackend } from "deepagents";

const agent = createDeepAgent({
  backend: new CompositeBackend(
    new StateBackend(),
    { "/memories/": new StoreBackend({
      namespace: ({ config }) => [
        String(config?.configurable?.langgraph_auth_user_id),
      ],
    }) },
  ),
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("expected agent");
console.log("✓ backends-composite-namespace-after validated");
// :remove-end:
