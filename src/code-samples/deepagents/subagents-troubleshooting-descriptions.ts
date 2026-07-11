// :snippet-start: subagents-troubleshooting-description-good-js
// ✅ Good
const goodDescription = {
  name: "research-specialist",
  description:
    "Conducts in-depth research on specific topics using web search. Use when you need detailed information that requires multiple searches.",
};
// :snippet-end:

// :snippet-start: subagents-troubleshooting-description-bad-js
// ❌ Bad
const badDescription = {
  name: "helper",
  description: "helps with stuff",
};
// :snippet-end:

// :remove-start:
import { createDeepAgent } from "deepagents";

const goodAgent = createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  subagents: [
    {
      systemPrompt: "You are a research specialist.",
      ...goodDescription,
    },
  ],
});
const badAgent = createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  subagents: [
    {
      systemPrompt: "You are a helper.",
      ...badDescription,
    },
  ],
});
if (!goodAgent || !badAgent) throw new Error("agent not created");
console.log("✓ subagents-troubleshooting-descriptions validated");
// :remove-end:
