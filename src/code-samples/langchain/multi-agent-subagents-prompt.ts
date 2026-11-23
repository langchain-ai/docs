// :remove-start:
process.env.OPENAI_API_KEY ??= "sk-test-key";

import { tool } from "langchain";
import { z } from "zod";

const task = tool(
  async ({ agentName, description }: { agentName: string; description: string }) => {
    return `Delegated "${description}" to ${agentName}`;
  },
  {
    name: "task",
    description: "Launch an ephemeral subagent for a task.",
    schema: z.object({
      agentName: z.string(),
      description: z.string(),
    }),
  },
);
// :remove-end:

// :snippet-start: multi-agent-subagents-prompt-js
import { createAgent } from "langchain";

const mainAgent = createAgent({
  model: "openai:gpt-5.4",
  tools: [task],
  systemPrompt: [
    "You coordinate specialized sub-agents.",
    "Available agents:",
    "- research: Research and fact-finding",
    "- writer: Content creation and editing",
    "- reviewer: Code and document review",
    "Use the task tool to delegate work.",
  ].join("\n"),
});
// :snippet-end:

// :remove-start:
if (!mainAgent) throw new Error("expected mainAgent");
console.log("✓ multi-agent-subagents-prompt validated");
// :remove-end:
