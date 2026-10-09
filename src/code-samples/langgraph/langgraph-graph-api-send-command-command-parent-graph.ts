// :snippet-start: langgraph-graph-api-send-command-command-parent-graph-js
import {
  StateGraph,
  StateSchema,
  ReducedValue,
  GraphNode,
  Command,
  START,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  foo: new ReducedValue(  // [!code highlight]
    z.string().default(""),
    { reducer: (x, y) => x + y }
  ),
});

const nodeA: GraphNode<{
  InputSchema: typeof State;
  Nodes: "nodeB" | "nodeC";
}> = (state) => {
  console.log("Called A");
  const value = Math.random() > 0.5 ? "a" : "b";
  const goto = value === "a" ? "nodeB" : "nodeC";

  return new Command({
    update: { foo: value },  // [!code highlight]
    goto,
    // Closest parent graph relative to this subgraph
    graph: Command.PARENT,
  });
};

const subgraph = new StateGraph(State)
  .addNode("nodeA", nodeA)
  .addEdge(START, "nodeA")
  .compile();

const nodeB: GraphNode<typeof State> = (state) => {
  console.log("Called B");
  // Reducer appends; do not manually concatenate onto state.foo
  return { foo: "b" };
};

const nodeC: GraphNode<typeof State> = (state) => {
  console.log("Called C");
  return { foo: "c" };
};

const graph = new StateGraph(State)
  .addNode("subgraph", subgraph, { ends: ["nodeB", "nodeC"] })
  .addNode("nodeB", nodeB)
  .addNode("nodeC", nodeC)
  .addEdge(START, "subgraph")
  .compile();
// :snippet-end:

// :snippet-start: langgraph-graph-api-send-command-command-parent-invoke-js
const result = await graph.invoke({ foo: "" });
console.log(result);
// :snippet-end:

// :remove-start:
// The docs snippet uses Math.random; pin it so both paths are asserted.
const originalRandom = Math.random;
try {
  Math.random = () => 0.9; // value "a" -> nodeB
  const viaB = await graph.invoke({ foo: "" });
  if (viaB.foo !== "ab") {
    throw new Error(`Expected "ab", got ${JSON.stringify(viaB)}`);
  }
  Math.random = () => 0.1; // value "b" -> nodeC
  const viaC = await graph.invoke({ foo: "" });
  if (viaC.foo !== "bc") {
    throw new Error(`Expected "bc", got ${JSON.stringify(viaC)}`);
  }
} finally {
  Math.random = originalRandom;
}
console.log("✓ langgraph-graph-api-send-command-command-parent-graph-js");
// :remove-end:
