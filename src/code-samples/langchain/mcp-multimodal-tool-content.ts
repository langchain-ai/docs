console.log("✓ multimodal ToolMessage contentBlocks work");
process.exit(0);
// :remove-end:

// :snippet-start: mcp-multimodal-tool-content-js
import { createAgent } from "langchain";

async function accessMultimodalToolContent(): Promise<void> {
  const { MultiServerMCPClient } = await import("@langchain/mcp-adapters");
  const client = new MultiServerMCPClient({});
  const tools = await client.getTools();
  const agent = createAgent({ model: "claude-sonnet-4-6", tools });

  const result = await agent.invoke({
    messages: [
      { role: "user", content: "Take a screenshot of the current page" },
    ],
  });

  // Access multimodal content from tool messages
  for (const message of result.messages) {
    if (message.type === "tool") {
      // Raw content in provider-native format
      console.log(`Raw content: ${message.content}`);

      // Standardized content blocks  // [!code highlight]
      for (const block of message.contentBlocks) {
        // [!code highlight]
        if (block.type === "text") {
          // [!code highlight]
          console.log(`Text: ${block.text}`); // [!code highlight]
        } else if (block.type === "image") {
          // [!code highlight]
          console.log(`Image URL: ${block.url}`); // [!code highlight]
          console.log(`Image base64: ${block.base64?.slice(0, 50)}...`); // [!code highlight]
        }
      }
    }
  }
}
// :snippet-end:
