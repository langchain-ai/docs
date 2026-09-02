// :snippet-start: deepagents-production-invoke-js
import { createDeepAgent } from "deepagents";
import { z } from "zod";

const contextSchema = z.object({ userId: z.string() });

const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  contextSchema,
});

// Start a conversation
const config = { configurable: { thread_id: crypto.randomUUID() } };
await agent.invoke(
  { messages: [{ role: "user", content: "Plan a 3-day trip to Tokyo" }] },
  { ...config, context: { userId: "user-123" } },
);

// Follow-up on the same conversation: reuse the same thread_id
await agent.invoke(
  { messages: [{ role: "user", content: "Make it 5 days instead" }] },
  { ...config, context: { userId: "user-123" } },
);
// :snippet-end:

// :remove-start:
async function main() {
  if (!agent) {
    throw new Error("expected agent");
  }
  console.log("✓ deep agent production invoke sample completed");
}

main();
// :remove-end:
