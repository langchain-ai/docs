// :snippet-start: backend-state-js
import { createDeepAgent, StateBackend } from "deepagents";

// By default we provide a StateBackend
const agent = createDeepAgent();

// Under the hood, it looks like
const agent2 = createDeepAgent({
  backend: new StateBackend(),
});
// :snippet-end:

// :remove-start:
if (!agent || !agent2) throw new Error("agents not created");
// :remove-end:
