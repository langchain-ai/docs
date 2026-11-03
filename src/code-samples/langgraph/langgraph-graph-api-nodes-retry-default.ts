// :remove-start:
import { END, START, StateGraph, StateSchema } from "@langchain/langgraph";
import * as z from "zod";

// Context for the snippet below, which shows only the `addNode` call.
const State = new StateSchema({
  count: z.number(),
});

let calls = 0;
const nodeFunction = () => {
  calls += 1;
  if (calls === 1) throw new Error("transient failure");
  return { count: calls };
};
// :remove-end:

// :snippet-start: langgraph-graph-api-nodes-retry-default-js
const builder = new StateGraph(State)
  .addNode("nodeName", nodeFunction, { retryPolicy: {} });
// :snippet-end:

// :remove-start:
if (!("nodeName" in builder.nodes)) throw new Error("nodeName missing");
const graph = builder
  .addEdge(START, "nodeName")
  .addEdge("nodeName", END)
  .compile();
const result = await graph.invoke({ count: 0 });
if (result.count !== 2 || calls !== 2) {
  throw new Error(`Expected one retry, got count=${result.count}, calls=${calls}`);
}
console.log("✓ langgraph-graph-api-nodes-retry-default-js validated");
// :remove-end:
