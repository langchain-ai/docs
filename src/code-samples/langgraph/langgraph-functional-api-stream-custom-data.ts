// :snippet-start: langgraph-functional-api-stream-custom-data-js
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

const config = {
  configurable: { thread_id: "functional-api-stream-custom-data" },
};

const stream = await main.stream(
  { x: 5 },
  { ...config, streamMode: "custom" },
);
for await (const chunk of stream) {
  console.log(chunk);
}
// Started processing
// Result is 10
// :snippet-end:

// :snippet-start: langgraph-functional-api-stream-values-js
const valuesStream = await main.streamEvents(
  { x: 5 },
  {
    configurable: { thread_id: "functional-api-stream-values" },
    version: "v3",
  },
);
for await (const snapshot of valuesStream.values) {
  console.log(snapshot);
}
// 10
// :snippet-end:

// :remove-start:
const testStream = await main.stream(
  { x: 5 },
  {
    configurable: { thread_id: "functional-api-stream-custom-data-test" },
    streamMode: "custom",
  },
);
const chunks = [];
for await (const chunk of testStream) {
  chunks.push(chunk);
}

if (
  JSON.stringify(chunks) !==
  JSON.stringify(["Started processing", "Result is 10"])
) {
  throw new Error(`Expected custom chunks, got ${JSON.stringify(chunks)}`);
}

const valuesTestStream = await main.streamEvents(
  { x: 5 },
  {
    configurable: { thread_id: "functional-api-stream-values-test" },
    version: "v3",
  },
);
const valuesChunks = [];
for await (const snapshot of valuesTestStream.values) {
  valuesChunks.push(snapshot);
}
if (JSON.stringify(valuesChunks) !== JSON.stringify([10])) {
  throw new Error(`Expected [10], got ${JSON.stringify(valuesChunks)}`);
}
console.log("✓ langgraph-functional-api-stream-custom-data-js");
// :remove-end:
