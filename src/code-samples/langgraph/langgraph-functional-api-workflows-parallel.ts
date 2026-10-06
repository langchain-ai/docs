// :snippet-start: langgraph-functional-api-workflows-parallel-js
import { entrypoint, MemorySaver, task } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const addOne = task("addOne", async (number: number) => {
  return number + 1;
});

const workflow = entrypoint(
  { checkpointer, name: "workflow" },
  async (numbers: number[]) => {
    return await Promise.all(numbers.map(addOne));
  }
);
// :snippet-end:

// :remove-start:
const parallel = await workflow.invoke([1, 2, 3], {
  configurable: { thread_id: "1" },
});
if (JSON.stringify(parallel) !== JSON.stringify([2, 3, 4])) {
  throw new Error(`expected [2,3,4], got ${JSON.stringify(parallel)}`);
}
console.log("✓ langgraph-functional-api-workflows-parallel");
// :remove-end:
