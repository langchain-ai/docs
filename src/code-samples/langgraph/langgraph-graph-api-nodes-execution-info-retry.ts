// :remove-start:
// Context for the snippet below. The primary call fails once, so the retry
// runs the node a second time with `nodeAttempt === 2`.
let primaryCalls = 0;
const callPrimaryApi = async (): Promise<string> => {
  primaryCalls += 1;
  throw new Error("primary unavailable");
};
const callFallbackApi = async (): Promise<string> => "fallback";
// :remove-end:

// :snippet-start: langgraph-graph-api-nodes-execution-info-retry-js
import { StateGraph, StateSchema, GraphNode, START, END } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  result: z.string(),
});

const myNode: GraphNode<typeof State> = async (state, config) => {
  const attempt = config.executionInfo?.nodeAttempt ?? 1;
  if (attempt > 1) {  // [!code highlight]
    // use a fallback on retries
    return { result: await callFallbackApi() };
  }
  return { result: await callPrimaryApi() };
};

const graph = new StateGraph(State)
  .addNode("my_node", myNode, { retryPolicy: { maxAttempts: 3 } })
  .addEdge(START, "my_node")
  .addEdge("my_node", END)
  .compile();
// :snippet-end:

// :remove-start:
const result = await graph.invoke({ result: "" });
if (result.result !== "fallback" || primaryCalls !== 1) {
  throw new Error(`Unexpected: ${result.result}, primaryCalls=${primaryCalls}`);
}
console.log("✓ langgraph-graph-api-nodes-execution-info-retry-js validated");
// :remove-end:
