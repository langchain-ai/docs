// :snippet-start: mcp-destructive-gate-js
import type { DynamicStructuredTool } from "@langchain/core/tools";
import { MemorySaver } from "@langchain/langgraph";
import { MCPAdapter } from "@langchain/mcp-adapters";
import type { ToolAnnotations } from "@modelcontextprotocol/client";
import {
  createAgent,
  humanInTheLoopMiddleware,
  type InterruptOnConfig,
  type WhenPredicate,
} from "langchain";

function isDestructive(tool: DynamicStructuredTool): boolean {
  const annotations = tool.metadata?.annotations as ToolAnnotations | undefined;
  return annotations?.destructiveHint ?? false;
}

async function gateDestructiveTools(serverUrl: string) {
  const adapter = new MCPAdapter({
    servers: { crm: { url: serverUrl } },
  });
  const tools = await adapter.listTools();

  // Read the hint once, then apply the same predicate to every tool call.
  const destructive = new Set(
    tools.filter(isDestructive).map((tool) => tool.name),
  );

  const needsApproval: WhenPredicate = (request) =>
    destructive.has(request.toolCall.name);

  const gate: InterruptOnConfig = {
    allowedDecisions: ["approve", "reject"],
    when: needsApproval,
  };
  const interruptOn = Object.fromEntries(
    tools.map((tool) => [tool.name, gate]),
  );

  const agent = createAgent({
    // KEEP MODEL
    model: "claude-sonnet-5",
    tools,
    middleware: [humanInTheLoopMiddleware({ interruptOn })],
    checkpointer: new MemorySaver(),
  });
  // :remove-start:
  assert.equal(destructive.has("crm_delete_file"), true);
  assert.equal(destructive.has("crm_list_files"), false);
  assert.deepEqual(gate.allowedDecisions, ["approve", "reject"]);
  assert.equal(interruptOn.crm_delete_file.when, needsApproval);
  assert.equal(interruptOn.crm_list_files.when, needsApproval);
  assert.ok(agent);
  // :remove-end:
  return { agent, adapter };
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
    const server = new McpServer({ name: "fixture", version: "1" });
    server.registerTool("list_files", { inputSchema: z.object({}) }, () => ({
      content: [{ type: "text", text: "report.md, notes.txt" }],
    }));
    server.registerTool(
      "delete_file",
      {
        inputSchema: z.object({ path: z.string() }),
        annotations: { destructiveHint: true },
      },
      ({ path }) => ({ content: [{ type: "text", text: `Deleted ${path}.` }] }),
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
  const { adapter } = await gateDestructiveTools(
    `http://127.0.0.1:${address.port}/mcp`,
  );
  await adapter.close();
  console.log("✓ mcp-destructive-gate: local MCP validation passed");
} finally {
  await handler.close();
  const closed = once(http, "close");
  http.close();
  http.closeAllConnections();
  await closed;
}
// :remove-end:
