// :snippet-start: skills-create-agent-js
import { createDeepAgent, FilesystemBackend } from "deepagents";

const backend = new FilesystemBackend({ rootDir: process.cwd() });

// KEEP MODEL
const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  backend,
  skills: ["/skills/"],
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ skills-create-agent sample validated");
// :remove-end:
