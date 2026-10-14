// :snippet-start: mcp-tool-errors-js
import { MCPAdapter } from "@langchain/mcp-adapters";
import { createAgent, ToolMessage } from "langchain";

async function divideByZero(serverUrl: string) {
  const adapter = new MCPAdapter({
    servers: { calculator: { url: serverUrl } },
  });

  try {
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
    const result = await agent.invoke({
      messages: [{ role: "user", content: "What is 10 divided by 0?" }],
    });

    // A server error (isError: true) reaches the model as a failed ToolMessage,
    // so the agent can read the server's own message and recover. By default,
    // createAgent also converts transport failures into error tool messages.
    for (const message of result.messages) {
      if (ToolMessage.isInstance(message) && message.status === "error") {
        console.log(`Tool error: ${message.text}`); // [!code highlight]
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
    id: "division-1",
    name: tools[0].name,
    args: { a: 10, b: 0 },
  });
  assert.ok(ToolMessage.isInstance(message));
  assert.equal(message.status, "error");
  assert.match(message.text, /zero/);
  await assert.rejects(() => tools[0].invoke({ a: 10, b: 0 }), /zero/);
}

const handler = createMcpHandler(
  () => {
    const server = new McpServer({ name: "fixture", version: "1" });
    server.registerTool(
      "divide",
      { inputSchema: z.object({ a: z.number(), b: z.number() }) },
      ({ a, b }) =>
        b === 0
          ? {
              isError: true,
              content: [{ type: "text", text: "Cannot divide by zero." }],
            }
          : { content: [{ type: "text", text: String(a / b) }] },
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
  await divideByZero(`http://127.0.0.1:${address.port}/mcp`);
  console.log("✓ mcp-tool-errors: local MCP validation passed");
} finally {
  await handler.close();
  const closed = once(http, "close");
  http.close();
  http.closeAllConnections();
  await closed;
}
// :remove-end:
