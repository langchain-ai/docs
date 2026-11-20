// :remove-start:
import { createDeepAgent, FilesystemBackend } from "deepagents";

const backend = new FilesystemBackend({ rootDir: process.cwd() });
const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  backend,
  skills: ["/skills/"],
});

console.log("✓ skills-pin-invoke sample validated");
process.exit(0);
// :remove-end:

// :snippet-start: skills-pin-invoke-js
const result = await agent.invoke(
  {
    messages: [{ role: "user", content: "What is LangGraph?" }],
    pinnedSkills: ["langgraph-docs"],
  },
  { configurable: { thread_id: "1" } },
);
// :snippet-end:
