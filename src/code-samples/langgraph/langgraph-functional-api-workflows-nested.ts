// :snippet-start: langgraph-functional-api-workflows-nested-js
import { entrypoint, MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

// Inherits the checkpointer when invoked from myWorkflow
const someOtherWorkflow = entrypoint(
  { name: "someOtherWorkflow" },
  async (inputs: { value: number }) => {
    return inputs.value;
  }
);

const myWorkflow = entrypoint(
  { checkpointer, name: "myWorkflow" },
  async (inputs: { value: number }) => {
    const value = await someOtherWorkflow.invoke({ value: 1 });
    return value;
  }
);
// :snippet-end:

// :remove-start:
const nested = await myWorkflow.invoke(
  { value: 0 },
  { configurable: { thread_id: "1" } }
);
if (nested !== 1) {
  throw new Error(`expected 1, got ${nested}`);
}
console.log("✓ langgraph-functional-api-workflows-nested");
// :remove-end:
