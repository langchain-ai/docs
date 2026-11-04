// :snippet-start: langgraph-functional-api-tasks-retry-js
import { entrypoint, task } from "@langchain/langgraph";
import type { RetryPolicy } from "@langchain/langgraph";

// Used only to simulate a transient failure. Do not use a variable like this in production.
let attempts = 0;

const retryPolicy: RetryPolicy = {
  retryOn: (error) => error instanceof Error,
};

const getInfo = task({ name: "getInfo", retry: retryPolicy }, () => {
  attempts += 1;

  if (attempts < 2) {
    throw new Error("Failure");
  }
  return "OK";
});

const main = entrypoint({ name: "main" }, async (inputs: Record<string, unknown>) => {
  return await getInfo();
});

console.log(await main.invoke({ any_input: "foobar" }));
// 'OK'
// :snippet-end:

// :remove-start:
const retryResult = await main.invoke({ any_input: "foobar" });
if (retryResult !== "OK") {
  throw new Error(`expected OK, got ${retryResult}`);
}
console.log("✓ langgraph-functional-api-tasks-retry");
// :remove-end:
