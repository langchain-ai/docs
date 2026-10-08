// :snippet-start: mcp-multi-server-js
import { MCPAdapter } from "@langchain/mcp-adapters";

async function listServerTools(calendarUrl: string, filesServerPath: string) {
  const adapter = new MCPAdapter({
    servers: {
      calendar: { url: calendarUrl },
      files: { command: "node", args: [filesServerPath] },
    },
  });

  try {
    const toolsets = await adapter.listToolsets();
    console.log(toolsets.calendar.map((tool) => tool.name));

    const fileTools = await adapter.listTools("files");
    console.log(fileTools.map((tool) => tool.name));
    // :remove-start:
    assert.deepEqual(Object.keys(toolsets), ["calendar", "files"]);
    assert.deepEqual(
      toolsets.calendar.map((tool) => tool.name),
      ["calendar_search"],
    );
    assert.deepEqual(
      fileTools.map((tool) => tool.name),
      ["files_search"],
    );
    assert.equal(await toolsets.calendar[0].invoke({}), "calendar");
    assert.equal(await fileTools[0].invoke({}), "files");
    // :remove-end:
  } finally {
    await adapter.close();
  }
}
// :snippet-end:

// :remove-start:
import assert from "node:assert/strict";
import { once } from "node:events";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { toNodeHandler } from "@modelcontextprotocol/node";
import { createMcpHandler, McpServer } from "@modelcontextprotocol/server";
import { z } from "zod/v4";

const handler = createMcpHandler(
  () => {
    const server = new McpServer({ name: "calendar", version: "1" });
    server.registerTool("search", { inputSchema: z.object({}) }, () => ({
      content: [{ type: "text", text: "calendar" }],
    }));
    return server;
  },
  { legacy: "reject" },
);
const http = createServer(toNodeHandler(handler));
http.listen(0, "127.0.0.1");
await once(http, "listening");
const address = http.address();
assert.ok(address && typeof address !== "string");
const directory = await mkdtemp(join(tmpdir(), "mcp-files-"));
try {
  const serverPath = join(directory, "files-server.mjs");
  await writeFile(
    serverPath,
    `
    import { McpServer } from ${JSON.stringify(import.meta.resolve("@modelcontextprotocol/server"))};
    import { serveStdio } from ${JSON.stringify(import.meta.resolve("@modelcontextprotocol/server/stdio"))};
    import { z } from ${JSON.stringify(import.meta.resolve("zod/v4"))};
    serveStdio(() => {
      const server = new McpServer({ name: "files", version: "1" });
      server.registerTool("search", { inputSchema: z.object({}) }, () => ({
        content: [{ type: "text", text: "files" }],
      }));
      return server;
    }, { legacy: "reject" });
  `,
  );
  await listServerTools(`http://127.0.0.1:${address.port}/mcp`, serverPath);
  console.log("✓ multiple servers: HTTP, stdio, selection, and distinct tool names");
} finally {
  await handler.close();
  const closed = once(http, "close");
  http.close();
  http.closeAllConnections();
  await closed;
  await rm(directory, { recursive: true, force: true });
}
// :remove-end:
