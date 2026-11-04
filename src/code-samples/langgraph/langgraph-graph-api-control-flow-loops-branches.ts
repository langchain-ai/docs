// :snippet-start: langgraph-graph-api-control-flow-loops-branches-js
import {
  StateGraph,
  StateSchema,
  ReducedValue,
  GraphNode,
  ConditionalEdgeRouter,
  START,
  END,
  GraphRecursionError,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  aggregate: new ReducedValue(z.array(z.string()).default(() => []), {
    reducer: (x, y) => x.concat(y),
  }),
});

const nodeA: GraphNode<typeof State> = (state) => {
  console.log(`Node A sees ${state.aggregate}`);
  return { aggregate: ["A"] };
};

const nodeB: GraphNode<typeof State> = (state) => {
  console.log(`Node B sees ${state.aggregate}`);
  return { aggregate: ["B"] };
};

const nodeC: GraphNode<typeof State> = (state) => {
  console.log(`Node C sees ${state.aggregate}`);
  return { aggregate: ["C"] };
};

const nodeD: GraphNode<typeof State> = (state) => {
  console.log(`Node D sees ${state.aggregate}`);
  return { aggregate: ["D"] };
};

const route: ConditionalEdgeRouter<{ InputSchema: typeof State; Nodes: "b" }> = (
  state
) => {
  if (state.aggregate.length < 7) {
    return "b";
  }
  return END;
};

const graph = new StateGraph(State)
  .addNode("a", nodeA)
  .addNode("b", nodeB)
  .addNode("c", nodeC)
  .addNode("d", nodeD)
  .addEdge(START, "a")
  .addConditionalEdges("a", route)
  .addEdge("b", "c")
  .addEdge("b", "d")
  .addEdge(["c", "d"], "a")
  .compile();
// :snippet-end:

// :snippet-start: langgraph-graph-api-control-flow-loops-branches-invoke-js
const result = await graph.invoke({ aggregate: [] });
// :snippet-end:

// :remove-start:
if (result.aggregate.join("") !== "ABCDABCDA") {
  throw new Error(`Unexpected aggregate: ${JSON.stringify(result.aggregate)}`);
}
// :remove-end:

// :snippet-start: langgraph-graph-api-control-flow-loops-branches-limit-js
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
console.log("✓ langgraph-graph-api-control-flow-loops-branches-js");
// :remove-end:
