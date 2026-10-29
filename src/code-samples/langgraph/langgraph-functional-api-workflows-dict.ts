// :snippet-start: langgraph-functional-api-workflows-dict-js
import { entrypoint, MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const myWorkflow = entrypoint(
  { checkpointer, name: "myWorkflow" },
  async (inputs: { value: number; anotherValue: number }) => {
    const value = inputs.value;
    const anotherValue = inputs.anotherValue;
    return { sum: value + anotherValue };
  }
);

await myWorkflow.invoke(
  { value: 1, anotherValue: 2 },
  { configurable: { thread_id: "1" } }
);
// :snippet-end:

// :remove-start:
const dictResult = await myWorkflow.invoke(
  { value: 1, anotherValue: 2 },
  { configurable: { thread_id: "2" } }
);
if (dictResult.sum !== 3) {
  throw new Error(`expected sum 3, got ${JSON.stringify(dictResult)}`);
}
console.log("✓ langgraph-functional-api-workflows-dict");
// :remove-end:
