// :snippet-start: skills-approval-js
import { MemorySaver } from "@langchain/langgraph";
import { createDeepAgent } from "deepagents";

// KEEP MODEL
const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  skills: ["/skills/personal/"],
  permissions: [
    {
      operations: ["write"],
      paths: ["/skills/**"],
      mode: "interrupt",
    },
  ],
  checkpointer: new MemorySaver(), // Required to pause and resume
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ skills-approval sample validated");
// :remove-end:
