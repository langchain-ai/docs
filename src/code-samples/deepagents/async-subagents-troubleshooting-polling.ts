// :remove-start:
import { type AsyncSubAgent } from "deepagents";

const asyncSubagents: AsyncSubAgent[] = [
  {
    name: "researcher",
    description: "Research agent",
    graphId: "researcher",
  },
];
// :remove-end:

// :snippet-start: async-subagents-troubleshooting-polling-js
import { createDeepAgent } from "deepagents";

// KEEP MODEL
const agent = createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  systemPrompt: `...your instructions...

    After launching an async subagent, ALWAYS return control to the user.
    Never call check_async_task immediately after launch.`,
  subagents: [...asyncSubagents],
});
// :snippet-end:

// :remove-start:
if (!agent) {
  throw new Error("agent not created");
}
console.log("✓ async-subagents-troubleshooting-polling sample validated");
// :remove-end:
