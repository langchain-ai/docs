// :snippet-start: subagents-troubleshooting-delegate-js
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  systemPrompt: `...your instructions...

  IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
  This keeps your context clean and improves results.`,
  subagents: [
    {
      name: "research-agent",
      description: "Conducts research",
      systemPrompt: "You are a researcher.",
    },
  ],
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ subagents-troubleshooting-delegate validated");
// :remove-end:
