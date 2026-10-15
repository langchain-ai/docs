// :snippet-start: mcp-quickstart-js
import { MCPAdapter } from "@langchain/mcp-adapters";
import { createAgent } from "langchain";

async function main() {
  const adapter = new MCPAdapter({
    servers: { docs: { url: "https://docs.langchain.com/mcp" } },
  });

  try {
    const tools = await adapter.listTools();
    // KEEP MODEL
    const agent = createAgent({ model: "claude-sonnet-5", tools });
    // :remove-start:
    assert.ok(tools.length > 0, "The docs server must expose tools.");
    assert.ok(agent);
    if (!process.env.ANTHROPIC_API_KEY) {
      console.log(
        "Docs tools discovered and agent constructed; model invocation not tested (no ANTHROPIC_API_KEY).",
      );
      return;
    }
    // :remove-end:
    const result = await agent.invoke({
      messages: [
        {
          role: "user",
          content: "How do I add short-term memory to a LangChain agent?",
        },
      ],
    });
    console.log(result.messages.at(-1)?.text);
  } finally {
    await adapter.close();
  }
}

await main();
// :snippet-end:

// :remove-start:
import assert from "node:assert/strict";

console.log(
  "✓ mcp-quickstart: tool discovery, agent construction, and cleanup",
);
// :remove-end:
