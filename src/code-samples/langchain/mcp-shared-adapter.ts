// :snippet-start: mcp-shared-adapter-js
import { MCPAdapter } from "@langchain/mcp-adapters";
import { createAgent } from "langchain";

// :remove-start:
import assert from "node:assert/strict";
import { once } from "node:events";
import { createServer } from "node:http";
import { toNodeHandler } from "@modelcontextprotocol/node";
import { createMcpHandler, McpServer } from "@modelcontextprotocol/server";
import { z } from "zod/v4";

const catalogs: Awaited<ReturnType<MCPAdapter["listTools"]>>[] = [];
const clients = new Set<unknown>();
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
// :remove-end:
const servers = {
  weather: { url: "https://example.com/mcp" },
};
// :remove-start:
servers.weather.url = `http://127.0.0.1:${address.port}/mcp`;
// :remove-end:
const adapter = new MCPAdapter({ servers });

export async function makeGraph() {
  const tools = await adapter.listTools([], { cacheMode: "refresh" });
  // :remove-start:
  catalogs.push(tools);
  clients.add(await adapter.getClient("weather"));
  assert.equal(await tools[0].invoke({ city: "Oslo" }), "Oslo: 18C and clear.");
  // :remove-end:
  return createAgent({
    // KEEP MODEL
    model: "claude-sonnet-5",
    tools,
  });
}
// :snippet-end:

// :remove-start:
try {
  const [first, second] = await Promise.all([makeGraph(), makeGraph()]);
  assert.ok(first);
  assert.ok(second);
  assert.equal(clients.size, 1, "Concurrent requests share one client");
  assert.ok([...clients][0]);
  const third = await makeGraph();
  assert.ok(third);
  assert.equal(clients.size, 1);
  assert.equal(catalogs[2][0], catalogs[1][0], "Unchanged tools reuse their wrappers");
  await adapter.close();
  await assert.rejects(() => catalogs[0][0].invoke({ city: "Oslo" }));
  console.log("✓ graph factory: module-scoped adapter reuse and cleanup");
} finally {
  await adapter.close();
  await handler.close();
  const closed = once(http, "close");
  http.close();
  http.closeAllConnections();
  await closed;
}
// :remove-end:
