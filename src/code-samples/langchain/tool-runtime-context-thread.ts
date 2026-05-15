// :snippet-start: tool-runtime-context-thread-js
import * as z from "zod";
import { v4 as uuidv4 } from "uuid";
import { ChatOpenAI } from "@langchain/openai";
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
  model: new ChatOpenAI({ model: "gpt-5.4" }),
  tools: [getUserName],
  contextSchema,
});

const result = await agent.invoke(
  {
    messages: [{ role: "user", content: "What is my name?" }],
  },
  {
    configurable: { thread_id: uuidv4() },
    context: { user_name: "John Smith" },
  },
);
// :snippet-end:

// :remove-start:
async function main() {
  const last = result.messages[result.messages.length - 1];
  const text =
    typeof last.content === "string"
      ? last.content
      : JSON.stringify(last.content);
  if (!text.includes("John Smith")) {
    throw new Error(`expected model to surface name, got: ${text}`);
  }
  console.log("✓ tool runtime context and thread_id invoke sample completed");
}

main();
// :remove-end:
