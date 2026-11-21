// :snippet-start: langgraph-graph-api-nodes-timeout-js
import {
  StateGraph,
  StateSchema,
  START,
  END,
  NodeTimeoutError,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  value: z.string(),
});

const callModel = async () => {
  await new Promise((resolve) => setTimeout(resolve, 2_000));
  return { value: "done" };
};

const graph = new StateGraph(State)
  .addNode("model", callModel, { timeout: 1_000 })
  // Or: { timeout: { runTimeout: 120_000, idleTimeout: 30_000 } }
  .addEdge(START, "model")
  .addEdge("model", END)
  .compile();

try {
  await graph.invoke({ value: "start" });
} catch (error) {
  if (error instanceof NodeTimeoutError) {
    console.log("Node timed out");
  }
}
// :snippet-end:

// :remove-start:
let timedOut = false;
try {
  await graph.invoke({ value: "start" });
} catch (error) {
  timedOut = error instanceof NodeTimeoutError;
}
if (!timedOut) throw new Error("Expected NodeTimeoutError");
console.log("✓ langgraph-graph-api-nodes-timeout-js validated");
// :remove-end:
