// :snippet-start: mcp-use-in-agent-js
import { MCPAdapter } from "@langchain/mcp-adapters";
import { createAgent } from "langchain";

async function main(server: string) {
  const adapter = new MCPAdapter({
    servers: { weather: { url: server } },
  });

  try {
    // Discover the server's tools, then hand them to the agent like any other
    // LangChain tools. Keep the adapter open while the agent calls its tools.
    const tools = await adapter.listTools();
    // :remove-start:
    await validateTools(tools);
    // :remove-end:
    // KEEP MODEL
    const agent = createAgent({ model: "claude-sonnet-5", tools });

    // :remove-start:
    assert.ok(agent);
    if (!process.env.ANTHROPIC_API_KEY) {
      console.log(
        "Agent constructed; model invocation not tested (no ANTHROPIC_API_KEY).",
      );
      return;
    }
    // :remove-end:
    await agent.invoke({
      messages: [{ role: "user", content: "What is the forecast for Oslo?" }],
    });
  } finally {
    await adapter.close();
  }
}
// :snippet-end:

// :remove-start:
import assert from "node:assert/strict";
import { once } from "node:events";
import { createServer } from "node:http";
import { toNodeHandler } from "@modelcontextprotocol/node";
import { createMcpHandler, McpServer } from "@modelcontextprotocol/server";
import { z } from "zod/v4";

async function validateTools(
  tools: Awaited<ReturnType<MCPAdapter["listTools"]>>,
) {
  assert.equal(tools.length, 1);
  assert.equal(await tools[0].invoke({ city: "Oslo" }), "Oslo: 18C and clear.");
}

const handler = createMcpHandler(
  () => {
    const server = new McpServer({ name: "fixture", version: "1" });
    server.registerTool(
      "get_forecast",
      { inputSchema: z.object({ city: z.string() }) },
      ({ city }) => ({
        content: [{ type: "text", text: `${city}: 18C and clear.` }],
      }),
    );
    return server;
  },
  { legacy: "reject" },
);
const http = createServer(toNodeHandler(handler));
http.listen(0, "127.0.0.1");
await once(http, "listening");
const address = http.address();
assert.ok(address && typeof address !== "string");
try {
  await main(`http://127.0.0.1:${address.port}/mcp`);
  console.log("✓ mcp-use-in-agent: local MCP validation passed");
} finally {
  await handler.close();
  const closed = once(http, "close");
  http.close();
  http.closeAllConnections();
  await closed;
}
// :remove-end:
