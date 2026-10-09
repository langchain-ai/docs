// :remove-start:
import {
  END,
  START,
  StateGraph,
  StateSchema,
  ReducedValue,
  GraphNode,
  ConditionalEdgeRouter,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  aggregate: new ReducedValue(z.array(z.string()).default(() => []), {
    reducer: (x, y) => x.concat(y),
  }),
});

const nodeA: GraphNode<typeof State> = () => ({ aggregate: ["A"] });
const nodeB: GraphNode<typeof State> = () => ({ aggregate: ["B"] });

const loopRoute: ConditionalEdgeRouter<{
  InputSchema: typeof State;
  Nodes: "b";
}> = (state) => (state.aggregate.length < 7 ? "b" : END);

const graph = new StateGraph(State)
  .addNode("a", nodeA)
  .addNode("b", nodeB)
  .addEdge(START, "a")
  .addConditionalEdges("a", loopRoute)
  .addEdge("b", "a")
  .compile();

const inputs = { aggregate: [] };
// :remove-end:

// :snippet-start: langgraph-graph-api-control-flow-loops-recursion-limit-js
import { GraphRecursionError } from "@langchain/langgraph";

try {
  await graph.invoke(inputs, { recursionLimit: 3 });
} catch (error) {
  if (error instanceof GraphRecursionError) {
    console.log("Recursion Error");
  }
}
// :snippet-end:

// :remove-start:
let raised = false;
try {
  await graph.invoke(inputs, { recursionLimit: 3 });
} catch (error) {
  raised = error instanceof GraphRecursionError;
}
if (!raised) {
  throw new Error("Expected GraphRecursionError at recursionLimit 3");
}
console.log("✓ langgraph-graph-api-control-flow-loops-recursion-limit-js");
// :remove-end:
