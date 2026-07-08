// :snippet-start: acp-custom-tools-js
import { DeepAgentsServer } from "deepagents-acp";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const searchTool = tool(
  async ({ query }) => {
    return `Results for: ${query}`;
  },
  {
    name: "search",
    description: "Search the codebase",
    schema: z.object({ query: z.string() }),
  },
);

const server = new DeepAgentsServer({
  agents: {
    name: "search-agent",
    tools: [searchTool],
  },
});

// :remove-start:
if (!server) {
  throw new Error("server not created");
}
console.log("✓ acp-custom-tools sample validated");
process.exit(0);
// :remove-end:

await server.start();
// :snippet-end:
