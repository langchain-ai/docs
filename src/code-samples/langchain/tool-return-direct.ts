// :snippet-start: tool-return-direct-js
import { ChatOpenAI } from "@langchain/openai";
import { createAgent, tool } from "langchain";
import * as z from "zod";

const fetchOrderStatus = tool(
  ({ order_id }) => {
    return `Order ${order_id} is shipped and will arrive in 2 days.`;
  },
  {
    name: "fetch_order_status",
    description: "Fetch the current status of a customer order.",
    schema: z.object({ order_id: z.string() }),
    returnDirect: true,
  },
);

const agent = createAgent({
  model: new ChatOpenAI({ model: "gpt-4o-mini" }),
  tools: [fetchOrderStatus],
});

const result = await agent.invoke({
  messages: [
    { role: "user", content: "What is the status of order #12345?" },
  ],
});
// The agent returns the tool output directly without another LLM call:
// "Order 12345 is shipped and will arrive in 2 days."
// :snippet-end:

// :remove-start:
async function main() {
  if (!fetchOrderStatus.returnDirect) {
    throw new Error("Expected fetchOrderStatus.returnDirect to be true");
  }

  const last = result.messages.at(-1);
  const content =
    typeof last?.content === "string"
      ? last.content
      : JSON.stringify(last?.content);

  if (!content.includes("shipped") || !content.includes("12345")) {
    throw new Error(
      `Expected direct tool output for order 12345, got: ${content}`,
    );
  }

  console.log("✓ returnDirect tool sample completed");
}

main();
// :remove-end:
