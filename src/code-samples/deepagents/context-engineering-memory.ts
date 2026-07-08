// :snippet-start: context-engineering-memory-js
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  memory: ["/project/AGENTS.md", "~/.deepagents/preferences.md"],
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ context-engineering-memory sample validated");
// :remove-end:
