// :snippet-start: langgraph-functional-api-hitl-pause-js
import {
  Command,
  MemorySaver,
  entrypoint,
  interrupt,
  task,
} from "@langchain/langgraph";

const step1 = task("step1", async (inputQuery: string) => {
  // Append bar
  return `${inputQuery} bar`;
});

const humanFeedback = task("humanFeedback", async (inputQuery: string) => {
  // Append user input
  const feedback = interrupt(`Please provide feedback: ${inputQuery}`);
  return `${inputQuery} ${feedback}`;
});

const step3 = task("step3", async (inputQuery: string) => {
  // Append qux
  return `${inputQuery} qux`;
});

const checkpointer = new MemorySaver();

const workflow = entrypoint(
  { checkpointer, name: "workflow" },
  async (inputQuery: string) => {
    const result1 = await step1(inputQuery);
    const result2 = await humanFeedback(result1);
    const result3 = await step3(result2);
    return result3;
  }
);

const config = { configurable: { thread_id: "1" } };

const stream = await workflow.streamEvents("foo", {
  ...config,
  version: "v3",
});
for await (const chunk of stream.values) {
  console.log(chunk);
}
// -> { __interrupt__: [{ value: 'Please provide feedback: foo bar', ... }] }

const resumed = await workflow.streamEvents(new Command({ resume: "baz" }), {
  ...config,
  version: "v3",
});
let last: unknown;
for await (const chunk of resumed.values) {
  console.log(chunk);
  last = chunk;
}
// -> 'foo bar baz qux'
// :snippet-end:

// :remove-start:
if (last !== "foo bar baz qux") {
  throw new Error(`expected foo bar baz qux, got ${JSON.stringify(last)}`);
}
console.log("✓ langgraph-functional-api-hitl-pause");
// :remove-end:
