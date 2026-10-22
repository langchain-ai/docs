// :remove-start:
import { FilesystemBackend } from "deepagents";

const backend = new FilesystemBackend({
  rootDir: "./my-project",
  virtualMode: true,
});
// :remove-end:

// :snippet-start: skills-tools-search-js
import { providerToolSearchMiddleware, tool } from "langchain";
import { createDeepAgent, createSkillsMiddleware } from "deepagents";
import { z } from "zod";

const createIssue = tool(async ({ team, title }) => `${team}-102: ${title}`, {
  name: "create_issue",
  description: "Create a Linear issue and return its ID.",
  schema: z.object({ team: z.string(), title: z.string() }),
  extras: { defer_loading: true },
});

// KEEP MODEL
const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  backend,
  tools: [createIssue],
  middleware: [
    providerToolSearchMiddleware(),
    createSkillsMiddleware({ backend, sources: ["/skills/"] }),
  ],
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ skills-tools-search sample validated");
// :remove-end:
