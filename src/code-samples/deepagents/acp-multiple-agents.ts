// :snippet-start: acp-multiple-agents-js
import { DeepAgentsServer } from "deepagents-acp";

const server = new DeepAgentsServer({
  agents: [
    { name: "code-agent", description: "General coding" },
    { name: "reviewer", description: "Code reviews" },
  ],
});
// :snippet-end:
