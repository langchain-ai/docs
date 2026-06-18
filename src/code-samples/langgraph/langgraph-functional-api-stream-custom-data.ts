import { entrypoint, MemorySaver } from "@langchain/langgraph";
import type { LangGraphRunnableConfig } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const main = entrypoint(
  { checkpointer, name: "main" },
  async (
    inputs: { x: number },
    config: LangGraphRunnableConfig,
  ): Promise<number> => {
    config.writer?.("Started processing");
    const result = inputs.x * 2;
    config.writer?.(`Result is ${result}`);
    return result;
  },
);

// :snippet-start: langgraph-functional-api-stream-custom-data-js
const config = {
  configurable: { thread_id: "functional-api-stream-custom-data" },
};

const stream = await main.streamEvents({ x: 5 }, { ...config, version: "v3" });
for await (const chunk of stream.values) {
  console.log(chunk);
}
// 10
// :snippet-end:

// :remove-start:
const testStream = await main.streamEvents(
  { x: 5 },
  { ...config, version: "v3" },
);
const chunks = [];
for await (const chunk of testStream.values) {
  chunks.push(chunk);
}

if (JSON.stringify(chunks) !== JSON.stringify([10])) {
  throw new Error(`Expected [10], got ${JSON.stringify(chunks)}`);
}
console.log("✓ langgraph-functional-api-stream-custom-data-js");
// :remove-end:
