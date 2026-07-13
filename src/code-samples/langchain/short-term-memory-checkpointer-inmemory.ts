// :snippet-start: short-term-memory-usage-js
import { createAgent, tool } from "langchain";
import { MemorySaver } from "@langchain/langgraph"; // [!code highlight]
import * as z from "zod";

const getUserInfo = tool(() => "No user profile on file.", {
  name: "get_user_info",
  description: "Look up information about the current user.",
  schema: z.object({}),
});

const checkpointer = new MemorySaver(); // [!code highlight]

const agent = createAgent({
  model: "openai:gpt-5.5",
  tools: [getUserInfo],
  checkpointer,
});

const threadConfig = { configurable: { thread_id: "1" } };
let result = await agent.invoke(
  { messages: [{ role: "user", content: "Hi! My name is Bob." }] },
  threadConfig, // [!code highlight]
);
let response = result.messages.at(-1)?.content;
console.log(response); // "Hi Bob! Nice to see you here. How are you doing?"

result = await agent.invoke(
  { messages: [{ role: "user", content: "What's my name?" }] },
  threadConfig, // [!code highlight]
);
response = result.messages.at(-1)?.content;
console.log(response); // "You are Bob!"
// :snippet-end:

// :remove-start:
function assistantText(content: unknown): string {
  if (typeof content === "string") {
    return content;
  }
  return "";
}

async function main() {
  const text = assistantText(response);
  if (!text.trim()) {
    throw new Error("expected non-empty assistant reply on second turn");
  }
  const humanCount = result.messages.filter((m) => m.type === "human").length;
  if (humanCount < 2) {
    throw new Error(`expected >=2 human turns, got ${humanCount}`);
  }
  if (!text.toLowerCase().includes("bob")) {
    throw new Error(
      "expected assistant to recall the name from the first turn",
    );
  }
  console.log(
    "✓ checkpointer persists conversation across turns on the same thread_id",
  );
}

main();
// :remove-end:
