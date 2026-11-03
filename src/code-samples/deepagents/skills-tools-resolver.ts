// :remove-start:
import { tool } from "langchain";
import { FilesystemBackend } from "deepagents";
import { z } from "zod";

const backend = new FilesystemBackend({
  rootDir: "./my-project",
  virtualMode: true,
});

const listIssues = tool(
  async ({ team }) => `${team}-101: Login page times out`,
  {
    name: "mcp_linear_list_issues_ab12",
    description: "List open issues for a Linear team.",
    schema: z.object({ team: z.string() }),
  },
);

const createIssue = tool(async ({ team, title }) => `${team}-102: ${title}`, {
  name: "mcp_linear_create_issue_cd34",
  description: "Create a Linear issue and return its ID.",
  schema: z.object({ team: z.string(), title: z.string() }),
});
// :remove-end:

// :snippet-start: skills-tools-resolver-js
import type { StructuredTool } from "langchain";
import {
  createDeepAgent,
  createSkillsMiddleware,
  type SkillToolResolver,
} from "deepagents";

// Real names like "mcp_linear_list_issues_ab12"
const toolsByName = new Map<string, StructuredTool>([
  ["list_issues", listIssues],
  ["create_issue", createIssue],
]);

const resolveSkillTools: SkillToolResolver = (name) => {
  const tool = toolsByName.get(name);
  return tool ? [tool] : [];
};

// KEEP MODEL
const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  backend,
  middleware: [
    createSkillsMiddleware({
      backend,
      sources: ["/skills/"],
      tools: resolveSkillTools,
    }),
  ],
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
const resolved = await resolveSkillTools("list_issues", {} as never);
if (resolved.map((t) => t.name).join() !== "mcp_linear_list_issues_ab12") {
  throw new Error(`unexpected tools: ${resolved.map((t) => t.name)}`);
}
if ((await resolveSkillTools("unknown", {} as never)).length !== 0) {
  throw new Error("expected no tools for an unknown name");
}
console.log("✓ skills-tools-resolver sample validated");
// :remove-end:
