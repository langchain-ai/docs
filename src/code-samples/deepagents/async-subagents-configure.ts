// :remove-start:
console.log("✓ async-subagents-configure sample validated");
process.exit(0);
// :remove-end:

// :snippet-start: async-subagents-configure-js
import { createDeepAgent, type AsyncSubAgent } from "deepagents";

const asyncSubagents: AsyncSubAgent[] = [
  {
    name: "researcher",
    description: "Research agent for information gathering and synthesis",
    graphId: "researcher",
    // No url → ASGI transport (co-deployed in the same deployment)
  },
  {
    name: "coder",
    description: "Coding agent for code generation and review",
    graphId: "coder",
    // url: "https://coder-deployment.langsmith.dev"  // Optional: HTTP transport for remote
  },
];

// KEEP MODEL
const agent = createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  subagents: [...asyncSubagents],
});
// :snippet-end:
