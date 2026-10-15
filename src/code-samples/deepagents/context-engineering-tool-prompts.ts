// :snippet-start: context-engineering-tool-prompts-js
import { tool } from "langchain";
import * as z from "zod";

const searchOrders = tool(
  async ({ userId, status, limit }) =>
    `orders for ${userId} with status ${status} (limit ${limit})`,
  {
    name: "search_orders",
    description: `Search for user orders by status.

Use this when the user asks about order history or wants to check
order status. Always filter by the provided status.`,
    schema: z.object({
      userId: z.string().describe("Unique identifier for the user"),
      status: z
        .enum(["pending", "shipped", "delivered"])
        .describe("Order status to filter by"),
      limit: z
        .number()
        .default(10)
        .describe("Maximum number of results to return"),
    }),
  },
);
// :snippet-end:

// :remove-start:

const directResult = await searchOrders.invoke({
  userId: "user-123",
  status: "pending",
  limit: 5,
});
if (!directResult.includes("user-123") || !directResult.includes("pending")) {
  throw new Error(`unexpected tool output: ${directResult}`);
}

console.log("✓ context-engineering-tool-prompts sample validated");
// :remove-end:
