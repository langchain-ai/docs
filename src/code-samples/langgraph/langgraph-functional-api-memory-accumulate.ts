// :snippet-start: langgraph-functional-api-memory-accumulate-js
import { entrypoint, getPreviousState, MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const accumulate = entrypoint(
  { checkpointer, name: "accumulate" },
  async (n: number) => {
    const previous = getPreviousState<number>() ?? 0;
    return previous + n;
  }
);

const config = { configurable: { thread_id: "1" } };
console.log(await accumulate.invoke(1, config)); // 1
console.log(await accumulate.invoke(2, config)); // 3
console.log(await accumulate.invoke(3, config)); // 6
// :snippet-end:

// :remove-start:
const next = await accumulate.invoke(0, config);
if (next !== 6) {
  throw new Error(`expected 6, got ${next}`);
}
console.log("✓ langgraph-functional-api-memory-accumulate");
// :remove-end:
