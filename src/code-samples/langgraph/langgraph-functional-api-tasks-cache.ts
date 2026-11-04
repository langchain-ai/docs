// :snippet-start: langgraph-functional-api-tasks-cache-js
import { entrypoint, task } from "@langchain/langgraph";
import { InMemoryCache } from "@langchain/langgraph-checkpoint";

const slowAdd = task(
  {
    name: "slowAdd",
    cache: { ttl: 120 },  // [!code highlight]
  },
  async (x: number) => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return x * 2;
  }
);

const main = entrypoint(
  { cache: new InMemoryCache(), name: "main" },
  async (inputs: { x: number }) => {
    const result1 = await slowAdd(inputs.x);
    const result2 = await slowAdd(inputs.x);
    return { result1, result2 };
  }
);

console.log(await main.invoke({ x: 5 }));
// { result1: 10, result2: 10 }
// :snippet-end:

// :remove-start:
const cached = await main.invoke({ x: 5 });
if (cached.result1 !== 10 || cached.result2 !== 10) {
  throw new Error(`expected { result1: 10, result2: 10 }, got ${JSON.stringify(cached)}`);
}
console.log("✓ langgraph-functional-api-tasks-cache");
// :remove-end:
