// :snippet-start: langgraph-functional-api-workflows-nested-extended-js
import { entrypoint, MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const multiply = entrypoint(
  { name: "multiply" },
  async (inputs: { a: number; b: number }) => {
    return inputs.a * inputs.b;
  }
);

const main = entrypoint(
  { checkpointer, name: "main" },
  async (inputs: { x: number; y: number }) => {
    const result = await multiply.invoke({ a: inputs.x, b: inputs.y });
    return { product: result };
  }
);

const config = { configurable: { thread_id: crypto.randomUUID() } };
console.log(await main.invoke({ x: 6, y: 7 }, config)); // { product: 42 }
// :snippet-end:

// :remove-start:
const product = await main.invoke({ x: 6, y: 7 }, config);
if (product.product !== 42) {
  throw new Error(`expected 42, got ${JSON.stringify(product)}`);
}
console.log("✓ langgraph-functional-api-workflows-nested-extended");
// :remove-end:
