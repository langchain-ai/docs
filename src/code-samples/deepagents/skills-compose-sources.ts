// :snippet-start: skills-compose-sources-js
import { createDeepAgent } from "deepagents";

// KEEP MODEL
const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  skills: ["/skills/org/", "/skills/team/", "/skills/request/"],
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ skills-compose-sources sample validated");
// :remove-end:
