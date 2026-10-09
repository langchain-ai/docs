// :snippet-start: langgraph-graph-api-overview-add-node-js
import { StateGraph, StateSchema, GraphNode } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  input: z.string(),
  results: z.string(),
});

const myNode: GraphNode<typeof State> = (state, config) => {
  return { results: `Hello, ${state.input}!` };
};

const builder = new StateGraph(State).addNode("myNode", myNode);
// :snippet-end:

// :remove-start:
import { END, START } from "@langchain/langgraph";

const graph = builder.addEdge(START, "myNode").addEdge("myNode", END).compile();
const result = await graph.invoke({ input: "Ada" });
if (result.results !== "Hello, Ada!") {
  throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
}
console.log("✓ langgraph-graph-api-overview-add-node-js");
// :remove-end:
