// :snippet-start: mcp-multimodal-tool-content-js
import { MultiServerMCPClient } from "@langchain/mcp-adapters";
import { createAgent } from "langchain";

async function accessMultimodalToolContent(): Promise<void> {
  const client = new MultiServerMCPClient({});
  const tools = await client.getTools();
  const agent = createAgent({ model: "claude-sonnet-4-6", tools });

  const result = await agent.invoke({
    messages: [{ role: "user", content: "Take a screenshot of the current page" }],
  });

  // Access multimodal content from tool messages
  for (const message of result.messages) {
    if (message.type === "tool") {
      // Raw content in provider-native format
      console.log(`Raw content: ${message.content}`);

      // Standardized content blocks  // [!code highlight]
      for (const block of message.contentBlocks) {  // [!code highlight]
        if (block.type === "text") {  // [!code highlight]
          console.log(`Text: ${block.text}`);  // [!code highlight]
        } else if (block.type === "image") {  // [!code highlight]
          console.log(`Image URL: ${block.url}`);  // [!code highlight]
          console.log(`Image base64: ${block.base64?.slice(0, 50)}...`);  // [!code highlight]
        }
      }
    }
  }
}
// :snippet-end:

// :remove-start:
import { ToolMessage } from "langchain";

function testMultimodalToolContentBlocks(): void {
  const message = new ToolMessage({
    content: [
      { type: "text", text: "Screenshot of the current page:" },
      { type: "image", url: "https://example.com/page.png" },
    ],
    tool_call_id: "call-1",
  });

  const textBlocks = message.contentBlocks.filter((block) => block.type === "text");
  const imageBlocks = message.contentBlocks.filter((block) => block.type === "image");

  if (textBlocks.length !== 1) {
    throw new Error(`Expected 1 text block, got ${textBlocks.length}`);
  }
  if (textBlocks[0].type !== "text" || textBlocks[0].text !== "Screenshot of the current page:") {
    throw new Error(`Unexpected text block: ${JSON.stringify(textBlocks[0])}`);
  }
  if (imageBlocks.length !== 1) {
    throw new Error(`Expected 1 image block, got ${imageBlocks.length}`);
  }
  if (imageBlocks[0].type !== "image" || imageBlocks[0].url !== "https://example.com/page.png") {
    throw new Error(`Unexpected image block: ${JSON.stringify(imageBlocks[0])}`);
  }
}

testMultimodalToolContentBlocks();
console.log("✓ multimodal ToolMessage contentBlocks work");
// :remove-end:
