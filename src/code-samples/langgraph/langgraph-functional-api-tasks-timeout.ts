// :snippet-start: langgraph-functional-api-tasks-timeout-js
import { entrypoint, task } from "@langchain/langgraph";

let attempts = 0;

const callApi = task(
  {
    name: "callApi",
    timeout: 1_000,
    retry: { maxAttempts: 3 },
  },
  async (url: string) => {
    attempts += 1;
    if (attempts < 2) {
      await new Promise((resolve) => setTimeout(resolve, 2_000));
    }
    return `result from ${url}`;
  }
);

const workflow = entrypoint(
  { name: "workflow", timeout: 5_000 },
  async (inputs: { url: string }) => {
    return await callApi(inputs.url);
  }
);

console.log(await workflow.invoke({ url: "https://example.com" }));
// 'result from https://example.com'
// :snippet-end:

// :remove-start:
const timeoutResult = await workflow.invoke({ url: "https://example.com" });
if (timeoutResult !== "result from https://example.com") {
  throw new Error(`unexpected timeout result: ${timeoutResult}`);
}
console.log("✓ langgraph-functional-api-tasks-timeout");
// :remove-end:
