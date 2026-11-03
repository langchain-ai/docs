// :snippet-start: mcp-protocol-eras-js
import { MCPAdapter } from "@langchain/mcp-adapters";

async function listToolsAcrossEras(modernUrl: string, legacyUrl: string) {
  const adapter = new MCPAdapter({
    servers: {
      current: { url: modernUrl, mode: "modern" },
      legacy: { url: legacyUrl, mode: "legacy" },
    },
  });

  try {
    const tools = await adapter.listTools();
    console.log(tools.map((tool) => tool.name));
    // :remove-start:
    assert.deepEqual(
      tools.map((tool) => tool.name),
      ["current_ping", "legacy_ping"],
    );
    assert.equal((await adapter.getClient("current"))?.getProtocolEra(), "modern");
    assert.equal((await adapter.getClient("legacy"))?.getProtocolEra(), "legacy");
    for (const tool of tools) assert.equal(await tool.invoke({}), "pong");
    // Exercise the exact call shown inline in the caching section.
    const refreshed = await adapter.listTools([], { cacheMode: "refresh" });
    assert.deepEqual(
      refreshed.map((tool) => tool.name),
      tools.map((tool) => tool.name),
    );
    // :remove-end:
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

const handler = createMcpHandler(
  () => {
    const server = new McpServer({ name: "protocol-eras", version: "1" });
    server.registerTool("ping", { inputSchema: z.object({}) }, () => ({
      content: [{ type: "text", text: "pong" }],
    }));
    return server;
  },
  { legacy: "stateless" },
);
const http = createServer(toNodeHandler(handler));
http.listen(0, "127.0.0.1");
await once(http, "listening");
const address = http.address();
assert.ok(address && typeof address !== "string");
try {
  const url = `http://127.0.0.1:${address.port}/mcp`;
  await listToolsAcrossEras(url, url);
  console.log("✓ protocol eras: independent negotiation, tool calls, and cache refresh");
} finally {
  await handler.close();
  const closed = once(http, "close");
  http.close();
  http.closeAllConnections();
  await closed;
}
// :remove-end:
