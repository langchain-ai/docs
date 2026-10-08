// :snippet-start: langgraph-functional-api-memory-final-js
import { entrypoint, getPreviousState, MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const accumulate = entrypoint(
  { checkpointer, name: "accumulate" },
  async (n: number) => {
    const previous = getPreviousState<number>() ?? 0;
    const total = previous + n;
    // Return the *previous* value to the caller but save the *new* total.
    return entrypoint.final({ value: previous, save: total });
  }
);

const config = { configurable: { thread_id: "my-thread" } };

console.log(await accumulate.invoke(1, config)); // 0
console.log(await accumulate.invoke(2, config)); // 1
console.log(await accumulate.invoke(3, config)); // 3
// :snippet-end:

// :snippet-start: langgraph-functional-api-memory-get-state-js
console.log(await accumulate.getState({
  configurable: {
    thread_id: "my-thread",  // [!code highlight]
    // optionally provide an ID for a specific checkpoint,
    // otherwise the latest checkpoint is shown
    // checkpoint_id: "1f1c1826-2179-626c-8004-96dc43069e17" [!code highlight]
  },
}));  // [!code highlight]
// :snippet-end:

// :snippet-start: langgraph-functional-api-memory-history-js
const history = [];  // [!code highlight]
for await (const state of accumulate.getStateHistory({
  configurable: {
    thread_id: "my-thread",  // [!code highlight]
  },
})) {
  history.push(state);
}
console.log(history[0]);
// :snippet-end:

// :snippet-start: langgraph-functional-api-memory-delete-js
await checkpointer.deleteThread("my-thread");
console.log(await accumulate.getState(config));
// StateSnapshot { values: {}, next: [], config: { configurable: { thread_id: 'my-thread' } }, ... }
// :snippet-end:

// :remove-start:
const afterDelete = await accumulate.getState(config);
if (JSON.stringify(afterDelete.values) !== "{}") {
  throw new Error(`expected empty values, got ${JSON.stringify(afterDelete.values)}`);
}
console.log("✓ langgraph-functional-api-memory-final");
// :remove-end:
