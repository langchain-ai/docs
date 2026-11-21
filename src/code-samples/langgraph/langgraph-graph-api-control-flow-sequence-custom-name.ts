// :remove-start:
import {
  START,
  StateGraph,
  StateSchema,
  GraphNode,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  value1: z.string(),
  value2: z.number(),
});

const step1: GraphNode<typeof State> = (state) => ({ value1: "a" });
// :remove-end:

// :snippet-start: langgraph-graph-api-control-flow-sequence-custom-name-js
const graph = new StateGraph(State)
  .addNode("myNode", step1)
  .addEdge(START, "myNode")
  .compile();
// :snippet-end:

// :remove-start:
if (!("myNode" in graph.nodes)) {
  throw new Error("Expected myNode to be registered");
}
console.log("✓ langgraph-graph-api-control-flow-sequence-custom-name-js");
// :remove-end:
