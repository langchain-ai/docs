// :remove-start:
import { tool } from "langchain";
import { FilesystemBackend } from "deepagents";
import path from "node:path";

const backend = new FilesystemBackend({
  rootDir: path.resolve("deepagents"),
  virtualMode: true,
});

/** Stand-in for your lookup, such as the user's own Linear MCP connection. */
function linearToolsForUser(userId: string) {
  return [
    tool(async ({ team }) => `${team}-101: Login page times out`, {
      name: "mcp_linear_list_issues_ab12",
      description: `List open issues for a Linear team, as ${userId}.`,
      schema: z.object({ team: z.string() }),
    }),
  ];
}
// :remove-end:

// :snippet-start: skills-tools-per-user-js
import {
  createDeepAgent,
  createSkillsMiddleware,
  type SkillToolResolver,
} from "deepagents";
import { z } from "zod";

const contextSchema = z.object({ userId: z.string() });

const resolveSkillTools: SkillToolResolver<z.infer<typeof contextSchema>> = (
  name,
  runtime,
) => {
  if (name !== "linear") return [];
  return linearToolsForUser(runtime.context.userId);
};

// KEEP MODEL
const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  backend,
  contextSchema,
  middleware: [
    createSkillsMiddleware({
      backend,
      sources: ["/skills/"],
      tools: resolveSkillTools,
    }),
  ],
});

const result = await agent.invoke(
  {
    messages: [
      { role: "user", content: "File a bug: checkout button does nothing." },
    ],
  },
  { context: { userId: "user-123" } },
);
// :snippet-end:

// :remove-start:
if (result.messages.length === 0) throw new Error("no messages returned");
console.log("✓ skills-tools-per-user sample validated");
// :remove-end:
