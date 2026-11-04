// :remove-start:
import { tool } from "langchain";
import {
  createSkillsMiddleware,
  FilesystemBackend,
  type SkillToolResolver,
} from "deepagents";
import { z } from "zod";

const backend = new FilesystemBackend({
  rootDir: "./my-project",
  virtualMode: true,
});

const linearTools = [
  tool(async ({ team }) => `${team}-101: Login page times out`, {
    name: "mcp_linear_list_issues_ab12",
    description: "List open issues for a Linear team.",
    schema: z.object({ team: z.string() }),
  }),
  tool(async ({ team, title }) => `${team}-102: ${title}`, {
    name: "mcp_linear_create_issue_cd34",
    description: "Create a Linear issue and return its ID.",
    schema: z.object({ team: z.string(), title: z.string() }),
  }),
];
// :remove-end:

// :snippet-start: skills-tools-integration-js
// Every tool from the Linear MCP server
const toolsByIntegration = new Map([["linear", linearTools]]);

const resolveSkillTools: SkillToolResolver = (name) =>
  toolsByIntegration.get(name) ?? [];
// :snippet-end:

// :remove-start:
if ((await resolveSkillTools("linear", {} as never)) !== linearTools) {
  throw new Error("expected every Linear tool");
}
if (
  !createSkillsMiddleware({
    backend,
    sources: ["/skills/"],
    tools: resolveSkillTools,
  })
) {
  throw new Error("middleware not created");
}
console.log("✓ skills-tools-integration sample validated");
// :remove-end:
