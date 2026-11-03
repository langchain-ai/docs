// :snippet-start: tool-runtime-context-thread-js
import * as z from "zod";
import { uuid7 } from "langsmith";
import { ChatOpenAI } from "@langchain/openai";
import { MemorySaver } from "@langchain/langgraph";
import { createAgent, tool } from "langchain";

const getUserName = tool(
  (_, config) => {
    return config.context.user_name;
  },
  {
    name: "get_user_name",
    description: "Get the user's name.",
    schema: z.object({}),
  },
);

const contextSchema = z.object({
  user_name: z.string(),
});

const agent = createAgent({
  model: new ChatOpenAI({ model: "gpt-5.5" }),
  tools: [getUserName],
  checkpointer: new MemorySaver(),
  contextSchema,
});

const threadId = uuid7();
const threadConfig = {
  configurable: { thread_id: threadId },
  context: { user_name: "John Smith" },
};

let result = await agent.invoke(
  {
    messages: [{ role: "user", content: "What is my name?" }],
  },
  threadConfig,
);
console.log(result.messages.at(-1)?.content);

result = await agent.invoke(
  {
    messages: [{ role: "user", content: "What was my name again?" }],
  },
  threadConfig,
);
console.log(result.messages.at(-1)?.content);
// :snippet-end:

// :remove-start:
async function main() {
  const last = result.messages[result.messages.length - 1];
  const text =
    typeof last.content === "string"
      ? last.content
      : (last.text ?? JSON.stringify(last.content));
  if (!text.includes("John Smith")) {
    throw new Error(`expected model to surface name, got: ${text}`);
  }
  console.log("✓ tool runtime context and thread_id invoke sample completed");
}

main();
// :remove-end:
