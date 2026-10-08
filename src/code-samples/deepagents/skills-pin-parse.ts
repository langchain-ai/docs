// :remove-start:
import { createDeepAgent, FilesystemBackend } from "deepagents";

const backend = new FilesystemBackend({ rootDir: process.cwd() });
const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  backend,
  skills: ["/skills/"],
});

console.log("✓ skills-pin-parse sample validated");
process.exit(0);
// :remove-end:

// :snippet-start: skills-pin-parse-js
const SKILL_REFERENCE = /(?<!\S)\/([a-z0-9-]+)/g;

const message = "/langgraph-docs How do I add a checkpointer to my graph?";
const pinnedSkills = [...message.matchAll(SKILL_REFERENCE)].map((m) => m[1]); // ["langgraph-docs"]

const result = await agent.invoke(
  {
    messages: [{ role: "user", content: message }],
    pinnedSkills,
  },
  { configurable: { thread_id: "1" } },
);
// :snippet-end:
