// :snippet-start: langgraph-functional-api-workflows-simple-js
import { entrypoint, task, MemorySaver } from "@langchain/langgraph";

const isEven = task("isEven", async (number: number) => {
  return number % 2 === 0;
});

const formatMessage = task("formatMessage", async (isEven: boolean) => {
  return isEven ? "The number is even." : "The number is odd.";
});

const checkpointer = new MemorySaver();

const workflow = entrypoint(
  { checkpointer, name: "workflow" },
  async (inputs: { number: number }) => {
    const even = await isEven(inputs.number);
    return await formatMessage(even);
  }
);

const config = { configurable: { thread_id: crypto.randomUUID() } };
const result = await workflow.invoke({ number: 7 }, config);
console.log(result);
// :snippet-end:

// :remove-start:
if (result !== "The number is odd.") {
  throw new Error(`expected odd message, got ${result}`);
}
console.log("✓ langgraph-functional-api-workflows-simple");
// :remove-end:
