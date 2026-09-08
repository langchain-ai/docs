// :snippet-start: async-subagents-hybrid-js
import type { AsyncSubAgent } from "deepagents";

const asyncSubagents: AsyncSubAgent[] = [
  {
    name: "researcher",
    description: "Research agent",
    graphId: "researcher",
    // No url → ASGI (co-deployed)
  },
  {
    name: "coder",
    description: "Coding agent",
    graphId: "coder",
    url: "https://coder-deployment.langsmith.dev",
    // url present → HTTP (remote)
  },
];
// :snippet-end:

// :remove-start:
if (asyncSubagents.length !== 2) {
  throw new Error("expected two async subagents");
}
console.log("✓ async-subagents-hybrid sample validated");
// :remove-end:
