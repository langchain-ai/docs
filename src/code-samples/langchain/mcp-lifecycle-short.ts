// :snippet-start: mcp-lifecycle-short-js
import { MCPAdapter } from "@langchain/mcp-adapters";
import { createAgent } from "langchain";

async function runAgent(serverUrl: string) {
  const adapter = new MCPAdapter({
    servers: { weather: { url: serverUrl } },
  });

  try {
    const tools = await adapter.listTools();
    // :remove-start:
    assert.deepEqual(
      tools.map((tool) => tool.name),
      ["weather__get_forecast"],
    );
    assert.equal(await tools[0].invoke({ city: "Oslo" }), "Oslo: 18C and clear.");
    issuedTool = tools[0];
    // :remove-end:
    const agent = createAgent({
      // KEEP MODEL
      model: "claude-sonnet-5-5",
      tools,
    });
    // :remove-start:
    assert.ok(agent);
    if (!process.env.ANTHROPIC_API_KEY) {
      console.log("Agent constructed; model invocation not tested (no ANTHROPIC_API_KEY).");
      return;
    }
    // :remove-end:
    const result = await agent.invoke({
      messages: [{ role: "user", content: "What is the weather in Oslo?" }],
    });
    console.log(result.messages.at(-1)?.text);
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

let issuedTool: Awaited<ReturnType<MCPAdapter["listTools"]>>[number] | undefined;
const handler = createMcpHandler(
  () => {
    const server = new McpServer({ name: "weather", version: "1" });
    server.registerTool(
      "get_forecast",
      { inputSchema: z.object({ city: z.string() }) },
      ({ city }) => ({ content: [{ type: "text", text: `${city}: 18C and clear.` }] }),
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
  await runAgent(`http://127.0.0.1:${address.port}/mcp`);
  assert.ok(issuedTool);
  await assert.rejects(() => issuedTool!.invoke({ city: "Oslo" }));
  console.log("✓ lifecycle: discovery, tool invocation, agent construction, and cleanup");
} finally {
  await handler.close();
  const closed = once(http, "close");
  http.close();
  http.closeAllConnections();
  await closed;
}
// :remove-end:
