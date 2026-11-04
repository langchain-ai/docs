// :snippet-start: langgraph-functional-api-workflows-parallel-llm-js
import { ChatAnthropic } from "@langchain/anthropic";
import { entrypoint, task, MemorySaver } from "@langchain/langgraph";

// :remove-start:
process.env.ANTHROPIC_API_KEY ??= "sk-ant-test-key";
import { FakeListChatModel } from "@langchain/core/utils/testing";
// :remove-end:
// KEEP MODEL
let model = new ChatAnthropic({ model: "claude-sonnet-4-6" });
// :remove-start:
model = new FakeListChatModel({
  responses: ["A paragraph.", "A paragraph.", "A paragraph."],
}) as unknown as ChatAnthropic;
// :remove-end:

const generateParagraph = task("generateParagraph", async (topic: string) => {
  const response = await model.invoke([
    { role: "system", content: "You are a helpful assistant that writes educational paragraphs." },
    { role: "user", content: `Write a paragraph about ${topic}.` }
  ]);
  return response.text;
});

const checkpointer = new MemorySaver();

const workflow = entrypoint(
  { checkpointer, name: "workflow" },
  async (topics: string[]) => {
    const paragraphs = await Promise.all(topics.map(generateParagraph));
    return paragraphs.join("\n\n");
  }
);

const config = { configurable: { thread_id: crypto.randomUUID() } };
const result = await workflow.invoke(["quantum computing", "climate change", "history of aviation"], config);
console.log(result);
// :snippet-end:

// :remove-start:
if (result !== "A paragraph.\n\nA paragraph.\n\nA paragraph.") {
  throw new Error(`unexpected result: ${result}`);
}
console.log("✓ langgraph-functional-api-workflows-parallel-llm");
// :remove-end:
