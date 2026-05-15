// :snippet-start: agent-invocation-thread-and-context-js
import { v4 as uuidv4 } from "uuid";
import * as z from "zod";
import { createAgent } from "langchain";
import { AIMessage } from "@langchain/core/messages";
import { FakeListChatModel } from "@langchain/core/utils/testing";
import { MemorySaver } from "@langchain/langgraph";

const contextSchema = z.object({
  user_id: z.string(),
});

const model = new FakeListChatModel({ responses: ["ok"] });

const agent = createAgent({
  model,
  tools: [],
  contextSchema,
  checkpointer: new MemorySaver(),
});

const result = await agent.invoke(
  {
    messages: [
      { role: "user", content: "What's the weather in San Francisco?" },
    ],
  },
  {
    configurable: { thread_id: uuidv4() },
    context: { user_id: "user-123" },
  },
);
// :snippet-end:

// :remove-start:
async function main() {
  const last = result.messages[result.messages.length - 1];
  if (!(last instanceof AIMessage)) {
    throw new Error("expected assistant message");
  }
  const blocks = last.contentBlocks ?? [];
  const text = blocks.find((b) => b.type === "text");
  const body =
    text && text.type === "text"
      ? text.text
      : typeof last.content === "string"
        ? last.content
        : "";
  if (body !== "ok") {
    throw new Error(`unexpected reply: ${body}`);
  }
  console.log("✓ thread_id and context invoke together without error");
}

main();
// :remove-end:
