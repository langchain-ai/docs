// :remove-start:
import { createDeepAgent } from "deepagents";

const testAgent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [],
});
if (!testAgent) throw new Error("agent not created");
console.log("✓ customization-mcp sample wiring validated");
process.exit(0);
// :remove-end:

// :snippet-start: customization-mcp-js
import { createDeepAgent } from "deepagents";

const { MultiServerMCPClient } = await import("@langchain/mcp-adapters");

const client = new MultiServerMCPClient({
    my_server: {
        transport: "http",
        url: "http://localhost:8000/mcp",
    },
});

const tools = await client.getTools();

const agent = await createDeepAgent({
    model: "openai:gpt-5.5",
    tools,
});

const result = await agent.invoke({
    messages: [{ role: "user", content: "Use the MCP server to help me." }],
});
// :snippet-end:
