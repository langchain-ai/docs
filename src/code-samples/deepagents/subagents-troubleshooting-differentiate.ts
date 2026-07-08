// :snippet-start: subagents-troubleshooting-differentiate-js
const subagents = [
  {
    name: "quick-researcher",
    description:
      "For simple, quick research questions that need 1-2 searches. Use when you need basic facts or definitions.",
    systemPrompt: "You are the quick-researcher subagent.",
  },
  {
    name: "deep-researcher",
    description:
      "For complex, in-depth research requiring multiple searches, synthesis, and analysis. Use for comprehensive reports.",
    systemPrompt: "You are the deep-researcher subagent.",
  },
];
// :snippet-end:

// :remove-start:
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  subagents,
});
if (!agent) throw new Error("agent not created");
console.log("✓ subagents-troubleshooting-differentiate validated");
// :remove-end:
