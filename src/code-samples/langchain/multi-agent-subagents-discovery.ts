// :remove-start:
process.env.OPENAI_API_KEY ??= "sk-test-key";

function searchAgentRegistry(query: string = "") {
  const agents = [
    { name: "research", description: "Research and fact-finding" },
    { name: "writer", description: "Content creation and editing" },
    { name: "reviewer", description: "Code and document review" },
  ];
  if (!query) return agents;
  return agents.filter(
    (agent) =>
      agent.name.includes(query) || agent.description.includes(query),
  );
}

function formatAgentList(
  agents: { name: string; description: string }[],
): string {
  return agents.map((agent) => `- ${agent.name}: ${agent.description}`).join("\n");
}
// :remove-end:

// :snippet-start: multi-agent-subagents-discovery-js
import { createAgent, tool } from "langchain";
import { z } from "zod";

const listAgents = tool(
  async ({ query = "" }) => {
    const agents = searchAgentRegistry(query);
    return formatAgentList(agents);
  },
  {
    name: "list_agents",
    description: "List available subagents, optionally filtered by query.",
    schema: z.object({ query: z.string().optional() }),
  }
);

const task = tool(
  async ({ agentName, description }) => {
    return `Delegated "${description}" to ${agentName}`;
  },
  {
    name: "task",
    description: "Launch an ephemeral subagent for a task.",
    schema: z.object({
      agentName: z.string(),
      description: z.string(),
    }),
  }
);

const mainAgent = createAgent({
  model: "openai:gpt-5.4",
  tools: [task, listAgents],
  systemPrompt:
    "Use list_agents to discover available subagents, then use task to invoke them.",
});
// :snippet-end:

// :remove-start:
if (!mainAgent) throw new Error("expected mainAgent");
console.log("✓ multi-agent-subagents-discovery validated");
// :remove-end:
