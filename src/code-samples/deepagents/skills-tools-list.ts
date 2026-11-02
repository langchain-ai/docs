// :snippet-start: skills-tools-list-js
import { tool } from "langchain";
import {
  createDeepAgent,
  createSkillsMiddleware,
  FilesystemBackend,
} from "deepagents";
import { z } from "zod";

const listIssues = tool(
  async ({ team }) => `${team}-101: Login page times out`,
  {
    name: "list_issues",
    description: "List open issues for a Linear team.",
    schema: z.object({ team: z.string() }),
  },
);

const createIssue = tool(async ({ team, title }) => `${team}-102: ${title}`, {
  name: "create_issue",
  description: "Create a Linear issue and return its ID.",
  schema: z.object({ team: z.string(), title: z.string() }),
});

const backend = new FilesystemBackend({
  rootDir: "./my-project",
  virtualMode: true,
});

// KEEP MODEL
const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  backend,
  middleware: [
    createSkillsMiddleware({
      backend,
      sources: ["/skills/"],
      tools: [listIssues, createIssue],
    }),
  ],
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ skills-tools-list sample validated");
// :remove-end:
