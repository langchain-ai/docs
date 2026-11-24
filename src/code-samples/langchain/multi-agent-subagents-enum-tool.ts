// :snippet-start: multi-agent-subagents-enum-tool-js
import { tool } from "langchain";
import { z } from "zod";

const task = tool(
  async ({ agentName, description }) => {
    return `Delegated "${description}" to ${agentName}`;
  },
  {
    name: "task",
    description: "Launch an ephemeral subagent for a task.",
    schema: z.object({
      agentName: z.enum(["research", "writer", "reviewer"]),
      description: z.string(),
    }),
  }
);
// :snippet-end:

// :remove-start:
if (!task) throw new Error("expected task tool");
console.log("✓ multi-agent-subagents-enum-tool validated");
// :remove-end:
