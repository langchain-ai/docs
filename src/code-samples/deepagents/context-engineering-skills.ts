// :snippet-start: context-engineering-skills-js
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({
  model: "google-genai:gemini-3.5-flash",
  skills: ["/skills/research/", "/skills/web-search/"],
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ context-engineering-skills sample validated");
// :remove-end:
