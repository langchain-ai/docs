// :remove-start:
// Setup that the docs snippet leaves out: state, a node function, and the
// edges that make the node reachable so the graph compiles.
import { END, START, StateGraph, StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  foo: z.string(),
});

const nodeFunction = (state: { foo: string }) => ({ foo: `${state.foo}!` });
// :remove-end:

// :snippet-start: langgraph-use-graph-api-node-config-js
const graph = new StateGraph(State)
  .addNode("nodeName", nodeFunction, { retryPolicy: {} })
  // :remove-start:
  .addEdge(START, "nodeName")
  .addEdge("nodeName", END)
  // :remove-end:
  .compile();
// :snippet-end:

// :remove-start:
const nodeConfigResult = await graph.invoke({ foo: "hi" });
if (nodeConfigResult.foo !== "hi!") {
  throw new Error(`expected "hi!", got ${nodeConfigResult.foo}`);
}
console.log("✓ langgraph-use-graph-api-node-config-js validated");
// :remove-end:
