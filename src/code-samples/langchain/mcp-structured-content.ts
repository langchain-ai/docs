// :snippet-start: mcp-structured-content-js
import { MCPAdapter } from "@langchain/mcp-adapters";
import { createAgent, ToolMessage } from "langchain";

async function readStructuredContent(serverUrl: string) {
  const adapter = new MCPAdapter({
    servers: { crm: { url: serverUrl } },
  });

  try {
    const tools = await adapter.listTools();
    // :remove-start:
    await validateTools(tools);
    // :remove-end:
    // KEEP MODEL
    const agent = createAgent({ model: "claude-sonnet-5-5", tools });
    // :remove-start:
    assert.ok(agent);
    if (!process.env.ANTHROPIC_API_KEY) {
      console.log(
        "Agent constructed; model invocation not tested (no ANTHROPIC_API_KEY).",
      );
      return;
    }
    // :remove-end:
    const result = await agent.invoke({
      messages: [{ role: "user", content: "Look up user 42." }],
    });

    // The adapter stores MCP result entries in an `artifact` array.
    // Find the `mcp_structured_content` entry, then read its `data` field.
    for (const message of result.messages) {
      if (ToolMessage.isInstance(message) && Array.isArray(message.artifact)) {
        const structured = message.artifact.find(
          (entry) => entry.type === "mcp_structured_content",
        );
        if (structured) {
          console.log(`Structured content: ${JSON.stringify(structured.data)}`); // [!code highlight]
        }
      }
    }
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
  const message = await tools[0].invoke({
    type: "tool_call",
    id: "user-1",
    name: tools[0].name,
    args: { user_id: 42 },
  });
  assert.ok(ToolMessage.isInstance(message));
  assert.ok(Array.isArray(message.artifact));
  const structured = message.artifact.find(
    (entry) => entry.type === "mcp_structured_content",
  );
  assert.deepEqual(structured?.data, { id: 42, name: "Alice", plan: "pro" });
}

const handler = createMcpHandler(
  () => {
    const server = new McpServer({ name: "fixture", version: "1" });
    server.registerTool(
      "get_user",
      { inputSchema: z.object({ user_id: z.number() }) },
      ({ user_id }) => ({
        content: [{ type: "text", text: "User found." }],
        structuredContent: { id: user_id, name: "Alice", plan: "pro" },
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
  await readStructuredContent(`http://127.0.0.1:${address.port}/mcp`);
  console.log("✓ mcp-structured-content: local MCP validation passed");
} finally {
  await handler.close();
  const closed = once(http, "close");
  http.close();
  http.closeAllConnections();
  await closed;
}
// :remove-end:
