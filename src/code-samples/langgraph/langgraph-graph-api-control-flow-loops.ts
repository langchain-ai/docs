// :snippet-start: langgraph-graph-api-control-flow-loops-define-js
import { StateGraph, StateSchema, ReducedValue, GraphNode, ConditionalEdgeRouter, START, END } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  // The reducer makes this append-only
  aggregate: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (x, y) => x.concat(y) }
  ),
});

const nodeA: GraphNode<typeof State> = (state) => {
  console.log(`Node A sees ${state.aggregate}`);
  return { aggregate: ["A"] };
};

const nodeB: GraphNode<typeof State> = (state) => {
  console.log(`Node B sees ${state.aggregate}`);
  return { aggregate: ["B"] };
};

// Define edges
const route: ConditionalEdgeRouter<{ InputSchema: typeof State; Nodes: "b" }> = (state) => {
  if (state.aggregate.length < 7) {
    return "b";
  } else {
    return END;
  }
};

const graph = new StateGraph(State)
  .addNode("a", nodeA)
  .addNode("b", nodeB)
  .addEdge(START, "a")
  .addConditionalEdges("a", route)
  .addEdge("b", "a")
  .compile();
// :snippet-end:

// :snippet-start: langgraph-graph-api-control-flow-loops-invoke-js
const result = await graph.invoke({ aggregate: [] });
console.log(result);
// :snippet-end:

// :remove-start:
if (result.aggregate.join("") !== "ABABABA") {
  throw new Error(`Unexpected aggregate: ${JSON.stringify(result.aggregate)}`);
}
// :remove-end:

// :snippet-start: langgraph-graph-api-control-flow-loops-impose-limit-js
import { GraphRecursionError } from "@langchain/langgraph";

try {
  await graph.invoke({ aggregate: [] }, { recursionLimit: 4 });
} catch (error) {
  if (error instanceof GraphRecursionError) {
    console.log("Recursion Error");
  }
}
// :snippet-end:

// :remove-start:
let raised = false;
try {
  await graph.invoke({ aggregate: [] }, { recursionLimit: 4 });
} catch (error) {
  raised = error instanceof GraphRecursionError;
}
if (!raised) {
  throw new Error("Expected GraphRecursionError at recursionLimit 4");
}
console.log("✓ langgraph-graph-api-control-flow-loops-js");
// :remove-end:
