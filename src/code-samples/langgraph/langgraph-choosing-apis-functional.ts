// :snippet-start: langgraph-choosing-apis-functional-js
// :codegroup-tab: Functional API
import { entrypoint, task } from "@langchain/langgraph";

const isEven = task("isEven", async (number: number) => {
  return number % 2 === 0;
});

const formatMessage = task("formatMessage", async (isEven: boolean) => {
  return isEven ? "The number is even." : "The number is odd.";
});

const workflow = entrypoint(
  { name: "workflow" },
  async (inputs: { number: number }) => {
    const even = await isEven(inputs.number);
    return await formatMessage(even);
  }
);

await workflow.invoke({ number: 7 });
// :snippet-end:

// :remove-start:
const functionalResult = await workflow.invoke({ number: 7 });
if (functionalResult !== "The number is odd.") {
  throw new Error(`expected odd message, got ${functionalResult}`);
}
console.log("✓ langgraph-choosing-apis-functional");
// :remove-end:
