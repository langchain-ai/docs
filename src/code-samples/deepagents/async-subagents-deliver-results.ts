// :snippet-start: async-subagents-deliver-results-js
import type { AsyncSubAgent } from "deepagents";

const asyncSubagents: AsyncSubAgent[] = [
  {
    name: "researcher",
    description: "Research agent for information gathering and synthesis",
    graphId: "researcher",
    webhook: "https://my-app.example.com/hooks/subagent-finished",
    notifyParent: false, // Your app delivers the result
  },
];
// :snippet-end:

// :remove-start:
if (asyncSubagents[0].notifyParent !== false) {
  throw new Error("expected notifyParent to be false");
}
console.log("✓ async-subagents-deliver-results sample validated");
// :remove-end:
