// :snippet-start: langgraph-functional-api-overview-inject-js
import {
  MemorySaver,
  InMemoryStore,
  entrypoint,
  getPreviousState,
} from "@langchain/langgraph";
import type { LangGraphRunnableConfig } from "@langchain/langgraph";

const checkpointer = new MemorySaver();
const store = new InMemoryStore();

const myWorkflow = entrypoint(
  { checkpointer, store, name: "workflow" },
  async (
    someInput: Record<string, unknown>,
    config: LangGraphRunnableConfig
  ) => {
    const previous = getPreviousState();
    const memoryStore = config.store;
    const writer = config.writer;
    return { previous, someInput };
  }
);
// :snippet-end:

// :remove-start:
const injectConfig = { configurable: { thread_id: "1" } };
const injectResult = await myWorkflow.invoke({ x: 1 }, injectConfig);
if (injectResult.previous !== undefined) {
  throw new Error(`expected undefined previous, got ${injectResult.previous}`);
}
if (JSON.stringify(injectResult.someInput) !== JSON.stringify({ x: 1 })) {
  throw new Error(JSON.stringify(injectResult.someInput));
}
console.log("✓ langgraph-functional-api-overview-inject");
// :remove-end:
