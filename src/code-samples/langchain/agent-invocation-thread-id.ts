// :snippet-start: agent-invocation-thread-id-js
import { v4 as uuidv4 } from "uuid";
import { createAgent } from "langchain";
import { AIMessage } from "@langchain/core/messages";
import { FakeListChatModel } from "@langchain/core/utils/testing";
import { MemorySaver } from "@langchain/langgraph";

const model = new FakeListChatModel({
  responses: [
    "First reply about San Francisco.",
    "Second reply about tomorrow.",
  ],
});

const agent = createAgent({
  model,
  tools: [],
  checkpointer: new MemorySaver(),
});

const config = { configurable: { thread_id: uuidv4() } };

let result = await agent.invoke(
  {
    messages: [
      { role: "user", content: "What's the weather in San Francisco?" },
    ],
  },
  config,
);

// A follow-up turn on the same conversation: reuse the same thread_id to keep history
result = await agent.invoke(
  { messages: [{ role: "user", content: "What about tomorrow?" }] },
  config,
);
// :snippet-end:

// :remove-start:
function lastAssistantText(): string {
  const last = result.messages[result.messages.length - 1];
  if (!(last instanceof AIMessage)) {
    throw new Error("expected final assistant message");
  }
  const blocks = last.contentBlocks ?? [];
  const textBlock = blocks.find((b) => b.type === "text");
  if (textBlock && textBlock.type === "text") {
    return textBlock.text;
  }
  return typeof last.content === "string" ? last.content : "";
}

async function main() {
  const humanCount = result.messages.filter((m) => m.type === "human").length;
  if (humanCount < 2) {
    throw new Error(`expected >=2 human turns, got ${humanCount}`);
  }
  const aiCount = result.messages.filter((m) => m.type === "ai").length;
  if (aiCount < 2) {
    throw new Error(`expected >=2 assistant replies, got ${aiCount}`);
  }
  if (!lastAssistantText()) {
    throw new Error("expected non-empty final assistant text");
  }
  console.log("✓ thread_id invocation persists conversation across turns");
}

main();
// :remove-end:
