// :snippet-start: mcp-multimodal-tool-content-v2-js
import { MCPAdapter } from "@langchain/mcp-adapters";
import { createAgent } from "langchain";

async function accessMultimodalToolContent(serverUrl: string) {
  const adapter = new MCPAdapter({
    servers: { browser: { url: serverUrl } },
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
      messages: [
        { role: "user", content: "Take a screenshot of the current page" },
      ],
    });

    // An MCP result arrives as LangChain content blocks. Image content
    // converts into standardized `image` blocks alongside `text`.
    for (const message of result.messages) {
      if (message.type === "tool") {
        for (const block of message.contentBlocks) { // [!code highlight]
          if (block.type === "text") { // [!code highlight]
            console.log(`Text: ${block.text}`); // [!code highlight]
          } else if (block.type === "image") { // [!code highlight]
            console.log(`Image MIME type: ${block.mimeType}`); // [!code highlight]
            console.log(`Image data: ${String(block.data).slice(0, 50)}...`); // [!code highlight]
          } // [!code highlight]
        } // [!code highlight]
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
import { ToolMessage } from "langchain";

const png =
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";

async function validateTools(
  tools: Awaited<ReturnType<MCPAdapter["listTools"]>>,
) {
  const message = await tools[0].invoke({
    type: "tool_call",
    id: "screenshot-1",
    name: tools[0].name,
    args: {},
  });
  assert.ok(ToolMessage.isInstance(message));
  const block = message.contentBlocks.find((block) => block.type === "image");
  assert.ok(block);
  assert.equal(block.mimeType, "image/png");
  assert.equal(block.data, png);
}

const handler = createMcpHandler(
  () => {
    const server = new McpServer({ name: "fixture", version: "1" });
    server.registerTool(
      "take_screenshot",
      { inputSchema: z.object({}) },
      () => ({
        content: [{ type: "image", data: png, mimeType: "image/png" }],
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
  await accessMultimodalToolContent(`http://127.0.0.1:${address.port}/mcp`);
  console.log("✓ mcp-multimodal-tool-content-v2: local MCP validation passed");
} finally {
  await handler.close();
  const closed = once(http, "close");
  http.close();
  http.closeAllConnections();
  await closed;
}
// :remove-end:
