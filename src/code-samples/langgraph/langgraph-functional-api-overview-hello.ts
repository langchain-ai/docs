// :snippet-start: langgraph-functional-api-overview-hello-js
import { MemorySaver, entrypoint } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const myWorkflow = entrypoint(
  { checkpointer, name: "workflow" },
  async (name: string): Promise<string> => {
    return `Hello, ${name}`;
  }
);

const config = { configurable: { thread_id: "1" } };
await myWorkflow.invoke("Alice", config); // "Hello, Alice"
// :snippet-end:

// :remove-start:
const hello = await myWorkflow.invoke("Alice", config);
if (hello !== "Hello, Alice") {
  throw new Error(hello);
}
console.log("✓ langgraph-functional-api-overview-hello");
// :remove-end:
