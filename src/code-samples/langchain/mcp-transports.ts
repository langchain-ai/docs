// :remove-start:
import assert from "node:assert/strict";
import { once } from "node:events";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { toNodeHandler } from "@modelcontextprotocol/node";
import { createMcpHandler, McpServer } from "@modelcontextprotocol/server";
import { SSEServerTransport } from "@modelcontextprotocol/server-legacy/sse";
import { z } from "zod/v4";

function weatherServer() {
  const server = new McpServer({ name: "weather", version: "1" });
  server.registerTool(
    "get_forecast",
    { inputSchema: z.object({ city: z.string() }) },
    ({ city }) => ({
      content: [{ type: "text", text: `${city}: 18C and clear.` }],
    }),
  );
  return server;
}

const handler = createMcpHandler(weatherServer, { legacy: "reject" });
const handleHttp = toNodeHandler(handler);
const sessions = new Map<string, SSEServerTransport>();
const sseServers = new Set<McpServer>();
const http = createServer(async (request, response) => {
  const url = new URL(request.url ?? "/", "http://127.0.0.1");
  try {
    if (url.pathname === "/sse" && request.method === "GET") {
      const transport = new SSEServerTransport("/messages", response);
      sessions.set(transport.sessionId, transport);
      response.on("close", () => sessions.delete(transport.sessionId));
      const server = weatherServer();
      sseServers.add(server);
      await server.connect(transport);
    } else if (url.pathname === "/messages" && request.method === "POST") {
      const transport = sessions.get(url.searchParams.get("sessionId") ?? "");
      if (transport) {
        await transport.handlePostMessage(request, response);
      } else {
        response.writeHead(400).end();
      }
    } else if (url.pathname === "/mcp") {
      await handleHttp(request, response);
    } else {
      response.writeHead(404).end();
    }
  } catch (error) {
    response.destroy(error instanceof Error ? error : undefined);
  }
});

const directory = await mkdtemp(join(tmpdir(), "mcp-transports-"));
const serverPath = join(directory, "weather-server.mjs");
await writeFile(
  serverPath,
  `
  import { McpServer } from ${JSON.stringify(import.meta.resolve("@modelcontextprotocol/server"))};
  import { serveStdio } from ${JSON.stringify(import.meta.resolve("@modelcontextprotocol/server/stdio"))};
  import { z } from ${JSON.stringify(import.meta.resolve("zod/v4"))};
  serveStdio(() => {
    const server = new McpServer({ name: "weather", version: "1" });
    server.registerTool(
      "get_forecast",
      { inputSchema: z.object({ city: z.string() }) },
      ({ city }) => ({ content: [{ type: "text", text: city + ": 18C and clear." }] }),
    );
    return server;
  }, { legacy: "reject" });
  `,
);
http.listen(0, "127.0.0.1");
await once(http, "listening");
const address = http.address();
assert.ok(address && typeof address !== "string");
const baseUrl = `http://127.0.0.1:${address.port}`;
const fixtureTargets: {
  local: { args?: string[] };
  remote: { url?: string };
  legacy: { url?: string };
} = {
  local: { args: [serverPath] },
  remote: { url: `${baseUrl}/mcp` },
  legacy: { url: `${baseUrl}/sse` },
};
// :remove-end:

// :snippet-start: mcp-transports-js
import { MCPAdapter } from "@langchain/mcp-adapters";

const adapter = new MCPAdapter({
  servers: {
    // A local server launched as a subprocess over stdio.
    local: {
      command: "node",
      args: ["./weather-server.js"],
      // :remove-start:
      // Replace only the placeholder target with the local test fixture.
      ...fixtureTargets.local,
      // :remove-end:
    },

    // A remote server reached over Streamable HTTP.
    remote: {
      url: "https://example.com/mcp",
      // :remove-start:
      ...fixtureTargets.remote,
      // :remove-end:
    },

    // A legacy server with an explicit SSE endpoint.
    legacy: {
      url: "https://legacy.example.com/sse",
      transport: "sse",
      mode: "legacy",
      // :remove-start:
      ...fixtureTargets.legacy,
      // :remove-end:
    },
  },
});

try {
  const tools = await adapter.listTools();
  // Pass tools to createAgent({ tools, ... }).
  // :remove-start:
  assert.deepEqual(tools.map((tool) => tool.name).sort(), [
    "legacy__get_forecast",
    "local__get_forecast",
    "remote__get_forecast",
  ]);
  for (const tool of tools) {
    assert.equal(await tool.invoke({ city: "Oslo" }), "Oslo: 18C and clear.");
  }
  assert.equal((await adapter.getClient("legacy"))?.getProtocolEra(), "legacy");
  console.log("✓ mcp-transports: stdio, Streamable HTTP, and SSE tool calls");
  // :remove-end:
} finally {
  await adapter.close();
  // :remove-start:
  await Promise.all([...sseServers].map((server) => server.close()));
  await handler.close();
  const closed = once(http, "close");
  http.close();
  http.closeAllConnections();
  await closed;
  await rm(directory, { recursive: true, force: true });
  // :remove-end:
}
// :snippet-end:
