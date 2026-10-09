// :snippet-start: langgraph-graph-api-send-command-command-graph-nodes-js
import { StateGraph, StateSchema, GraphNode, Command, START } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  foo: z.string(),
});

const nodeA: GraphNode<{
  InputSchema: typeof State;
  Nodes: "nodeB" | "nodeC";
}> = (state) => {
  console.log("Called A");
  const value = Math.random() > 0.5 ? "b" : "c";
  const goto = value === "b" ? "nodeB" : "nodeC";

  return new Command({
    update: { foo: value },
    goto,
  });
};

const nodeB: GraphNode<typeof State> = (state) => {
  console.log("Called B");
  return { foo: state.foo + "b" };
};

const nodeC: GraphNode<typeof State> = (state) => {
  console.log("Called C");
  return { foo: state.foo + "c" };
};
// :snippet-end:

// :snippet-start: langgraph-graph-api-send-command-command-graph-build-js
const graph = new StateGraph(State)
  .addNode("nodeA", nodeA, {
    ends: ["nodeB", "nodeC"],
  })
  .addNode("nodeB", nodeB)
  .addNode("nodeC", nodeC)
  .addEdge(START, "nodeA")
  .compile();
// :snippet-end:

// :snippet-start: langgraph-graph-api-send-command-command-graph-invoke-js
const result = await graph.invoke({ foo: "" });
console.log(result);
// :snippet-end:

// :remove-start:
// The docs snippet uses Math.random; pin it so both paths are asserted.
const originalRandom = Math.random;
try {
  Math.random = () => 0.9; // value "b" -> nodeB
  const viaB = await graph.invoke({ foo: "" });
  if (viaB.foo !== "bb") {
    throw new Error(`Expected "bb", got ${JSON.stringify(viaB)}`);
  }
  Math.random = () => 0.1; // value "c" -> nodeC
  const viaC = await graph.invoke({ foo: "" });
  if (viaC.foo !== "cc") {
    throw new Error(`Expected "cc", got ${JSON.stringify(viaC)}`);
  }
} finally {
  Math.random = originalRandom;
}

const drawable = await graph.getGraphAsync();
const edges = drawable.edges.map((e) => `${e.source}->${e.target}`);
if (!edges.includes("nodeA->nodeB") || !edges.includes("nodeA->nodeC")) {
  throw new Error(`Expected nodeA edges to nodeB and nodeC, got ${edges}`);
}
console.log("✓ langgraph-graph-api-send-command-command-graph-js");
// :remove-end:
