// :remove-start:
import {
  END,
  START,
  StateGraph,
  StateSchema,
} from "@langchain/langgraph";
import * as z from "zod";

const InputState = new StateSchema({ userInput: z.string() });
const OutputState = new StateSchema({ graphOutput: z.string() });
const OverallState = new StateSchema({
  foo: z.string(),
  userInput: z.string(),
  graphOutput: z.string(),
});
const PrivateState = new StateSchema({ bar: z.string() });

const graph = new StateGraph({
  state: OverallState,
  input: InputState,
  output: OutputState,
})
  .addNode("node1", (state) => ({ foo: state.userInput + " name" }))
  .addNode("node2", (state) => ({ bar: state.foo + " is" }))
  .addNode("node3", (state) => ({ graphOutput: state.bar + " Lance" }), {
    input: PrivateState,
  })
  .addEdge(START, "node1")
  .addEdge("node1", "node2")
  .addEdge("node2", "node3")
  .addEdge("node3", END)
  .compile();
// :remove-end:

// :snippet-start: langgraph-graph-api-state-stream-output-keys-js
for await (const snapshot of await graph.stream(
  { userInput: "My" },
  { streamMode: "values", outputKeys: ["graphOutput"] }, // [!code highlight]
)) {
  console.log(snapshot);
}
// { graphOutput: 'My name is Lance' }
// :snippet-end:

// :remove-start:
async function main() {
  const snapshots: Array<Record<string, unknown>> = [];
  for await (const snapshot of await graph.stream(
    { userInput: "My" },
    { streamMode: "values", outputKeys: ["graphOutput"] },
  )) {
    snapshots.push(snapshot as Record<string, unknown>);
  }
  const last = snapshots[snapshots.length - 1];
  if (JSON.stringify(last) !== JSON.stringify({ graphOutput: "My name is Lance" })) {
    throw new Error(`Unexpected final snapshot: ${JSON.stringify(last)}`);
  }
  if (snapshots.some((s) => Object.keys(s).some((k) => k !== "graphOutput"))) {
    throw new Error(`Unexpected keys: ${JSON.stringify(snapshots)}`);
  }
  console.log("✓ langgraph-graph-api-state-stream-output-keys-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
