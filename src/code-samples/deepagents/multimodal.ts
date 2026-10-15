// :remove-start:
const agent = {
  invoke: async (_input: unknown) => ({ messages: [] }),
};
// :remove-end:

// :snippet-start: multimodal-user-input-js
const result = await agent.invoke({
  messages: [
    {
      role: "user",
      content: [
        { type: "text", text: "What is in this screenshot?" },
        { type: "image", url: "https://example.com/screenshot.png" },
      ],
    },
  ],
});
// :snippet-end:

// :remove-start:
if (!result) throw new Error("expected invoke result");
// :remove-end:

// :snippet-start: multimodal-capture-screenshot-js
import { tool } from "langchain";
import { z } from "zod";

const captureScreenshot = tool(
  async () => [
    { type: "text", text: "Screenshot of the current page:" },
    { type: "image", url: "https://example.com/page.png" },
  ],
  {
    name: "capture_screenshot",
    description: "Capture a screenshot of the current page.",
    schema: z.object({}),
  },
);
// :snippet-end:

// :remove-start:
const blocks = await captureScreenshot.invoke({});
if (!Array.isArray(blocks) || blocks.length !== 2) {
  throw new Error("expected two content blocks");
}
// :remove-end:
