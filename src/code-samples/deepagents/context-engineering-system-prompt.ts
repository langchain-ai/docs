// :snippet-start: context-engineering-system-prompt-js
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({
  model: "google-genai:gemini-3.5-flash",
  systemPrompt: `You are a research assistant specializing in scientific literature.
  Always cite sources. Use subagents for parallel research on different topics.`,
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ context-engineering-system-prompt sample validated");
// :remove-end:
