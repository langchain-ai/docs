// :snippet-start: langgraph-graph-api-overview-compile-js
import { END, START, StateGraph, StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  text: z.string(),
});

const graph = new StateGraph(State)
  .addNode("nodeA", (state) => ({ text: `${state.text}a` }))
  .addEdge(START, "nodeA")
  .addEdge("nodeA", END)
  .compile();

await graph.invoke({ text: "" });
// { text: 'a' }
// :snippet-end:

// :remove-start:
const result = await graph.invoke({ text: "" });
if (result.text !== "a") {
  throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
}
console.log("✓ langgraph-graph-api-overview-compile-js");
// :remove-end:
