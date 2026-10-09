// :snippet-start: langgraph-graph-api-state-private-state-js
import { StateGraph, StateSchema, GraphNode, START, END } from "@langchain/langgraph";
import * as z from "zod";

// The overall state of the graph (this is the public state shared across nodes)
const OverallState = new StateSchema({
  a: z.string(),
});

// Output from node1 contains private data that is not part of the overall state
const Node1Output = new StateSchema({
  privateData: z.string(),
});

// Node 2 input only requests the private data available after node1
const Node2Input = new StateSchema({
  privateData: z.string(),
});

// The private data is only shared between node1 and node2
const node1: GraphNode<typeof OverallState> = (state) => {
  const output = { privateData: "set by node1" };
  console.log(`Entered node 'node1':\n\tInput: ${JSON.stringify(state)}.\n\tReturned: ${JSON.stringify(output)}`);
  return output;
};

const node2: GraphNode<typeof Node2Input> = (state) => {
  const output = { a: "set by node2" };
  console.log(`Entered node 'node2':\n\tInput: ${JSON.stringify(state)}.\n\tReturned: ${JSON.stringify(output)}`);
  return output;
};

// Node 3 only has access to the overall state (no access to private data from node1)
const node3: GraphNode<typeof OverallState> = (state) => {
  const output = { a: "set by node3" };
  console.log(`Entered node 'node3':\n\tInput: ${JSON.stringify(state)}.\n\tReturned: ${JSON.stringify(output)}`);
  return output;
};

// Connect nodes in a sequence
// node2 accepts private data from node1, whereas
// node3 does not see the private data.
const graph = new StateGraph(OverallState)
  .addNode("node1", node1)
  .addNode("node2", node2, { input: Node2Input })
  .addNode("node3", node3)
  .addEdge(START, "node1")
  .addEdge("node1", "node2")
  .addEdge("node2", "node3")
  .addEdge("node3", END)
  .compile();

// Invoke the graph with the initial state
const response = await graph.invoke({ a: "set at start" });

console.log(`\nOutput of graph invocation: ${JSON.stringify(response)}`);
// :snippet-end:

// :remove-start:
async function main() {
  if (JSON.stringify(response) !== JSON.stringify({ a: "set by node3" })) {
    throw new Error(`Unexpected response: ${JSON.stringify(response)}`);
  }
  console.log("✓ langgraph-graph-api-state-private-state-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
