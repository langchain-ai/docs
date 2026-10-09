// :snippet-start: langgraph-graph-api-control-flow-branches-parallel-js
import { StateGraph, StateSchema, ReducedValue, GraphNode, START, END } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  // The reducer makes this append-only
  aggregate: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (x, y) => x.concat(y) }
  ),
});

const nodeA: GraphNode<typeof State> = (state) => {
  console.log(`Adding "A" to ${state.aggregate}`);
  return { aggregate: ["A"] };
};

const nodeB: GraphNode<typeof State> = (state) => {
  console.log(`Adding "B" to ${state.aggregate}`);
  return { aggregate: ["B"] };
};

const nodeC: GraphNode<typeof State> = (state) => {
  console.log(`Adding "C" to ${state.aggregate}`);
  return { aggregate: ["C"] };
};

const nodeD: GraphNode<typeof State> = (state) => {
  console.log(`Adding "D" to ${state.aggregate}`);
  return { aggregate: ["D"] };
};

const graph = new StateGraph(State)
  .addNode("a", nodeA)
  .addNode("b", nodeB)
  .addNode("c", nodeC)
  .addNode("d", nodeD)
  .addEdge(START, "a")
  .addEdge("a", "b")
  .addEdge("a", "c")
  .addEdge("b", "d")
  .addEdge("c", "d")
  .addEdge("d", END)
  .compile();
// :snippet-end:

// :snippet-start: langgraph-graph-api-control-flow-branches-parallel-invoke-js
const result = await graph.invoke({
  aggregate: [],
});
console.log(result);
// :snippet-end:

// :remove-start:
const aggregate = result.aggregate;
if (
  aggregate.length !== 4 ||
  aggregate[0] !== "A" ||
  aggregate[3] !== "D" ||
  [...aggregate.slice(1, 3)].sort().join() !== "B,C"
) {
  throw new Error(`Unexpected aggregate: ${JSON.stringify(aggregate)}`);
}
console.log("✓ langgraph-graph-api-control-flow-branches-parallel-js");
// :remove-end:
