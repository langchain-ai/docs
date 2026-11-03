// :snippet-start: langgraph-functional-api-overview-task-exec-js
import { MemorySaver, entrypoint, task } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const slowComputation = task("slowComputation", async (inputValue: number) => {
  return inputValue * 2;
});

const myWorkflow = entrypoint(
  { checkpointer, name: "workflow" },
  async (someInput: number): Promise<number> => {
    return await slowComputation(someInput);
  }
);
// :snippet-end:

// :remove-start:
const doubled = await myWorkflow.invoke(3, {
  configurable: { thread_id: "1" },
});
if (doubled !== 6) {
  throw new Error(`expected 6, got ${doubled}`);
}
console.log("✓ langgraph-functional-api-overview-task-exec");
// :remove-end:
