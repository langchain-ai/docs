// :snippet-start: acp-deep-agents-server-js
import { DeepAgentsServer } from "deepagents-acp";

const server = new DeepAgentsServer({
  agents: [
    {
      name: "code-agent",
      description: "Full-featured coding assistant",
      model: "claude-sonnet-4-5-20250929",
      skills: ["./skills/"],
      memory: ["./.deepagents/AGENTS.md"],
    },
    {
      name: "reviewer",
      description: "Code review specialist",
      systemPrompt: "You are a code review expert...",
    },
  ],
  serverName: "my-deepagents-acp",
  serverVersion: "1.0.0",
  workspaceRoot: process.cwd(),
  debug: true,
});

// :remove-start:
if (!server) {
  throw new Error("server not created");
}
console.log("✓ acp-deep-agents-server sample validated");
process.exit(0);
// :remove-end:
await server.start();
// :snippet-end:
