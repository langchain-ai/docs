// :remove-start:
import { Command, END, NodeError, StateSchema } from "@langchain/langgraph";
import * as z from "zod";

// Context for the snippet below.
const State = new StateSchema({
  result: z.string(),
});

const nodeA = async () => ({ result: "a" });
const nodeB = async () => ({ result: "b" });
const fallbackHandler = async (state: typeof State.State, error: NodeError) =>
  new Command({ update: { result: "fallback" }, goto: END });
// :remove-end:

// :snippet-start: langgraph-graph-api-nodes-node-defaults-js
import { StateGraph, START } from "@langchain/langgraph";

const graph = new StateGraph(State)
  .setNodeDefaults({
    retryPolicy: { maxAttempts: 3 },
    timeout: { runTimeout: 30_000 },
    errorHandler: fallbackHandler,
  })
  .addNode("a", nodeA)
  .addNode("b", nodeB, { retryPolicy: { maxAttempts: 5 } }) // overrides default
  .addEdge(START, "a")
  .compile();
// :snippet-end:

// :remove-start:
if (!("a" in graph.nodes) || !("b" in graph.nodes)) {
  throw new Error("Expected nodes a and b");
}
const result = await graph.invoke({ result: "" });
if (result.result !== "a") throw new Error(`Unexpected result: ${result.result}`);
console.log("✓ langgraph-graph-api-nodes-node-defaults-js validated");
// :remove-end:
