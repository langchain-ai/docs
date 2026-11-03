// :snippet-start: langgraph-graph-api-nodes-execution-info-ids-js
import { StateGraph, StateSchema, GraphNode, START, END } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  result: z.string(),
});

const myNode: GraphNode<typeof State> = async (state, config) => {
  const info = config.executionInfo;
  console.log(`Thread: ${info?.threadId}, Run: ${info?.runId}`);  // [!code highlight]
  return { result: "done" };
};

const graph = new StateGraph(State)
  .addNode("my_node", myNode)
  .addEdge(START, "my_node")
  .addEdge("my_node", END)
  .compile();
// :snippet-end:

// :remove-start:
const result = await graph.invoke({ result: "" });
if (result.result !== "done") throw new Error(`Unexpected result: ${result.result}`);
console.log("✓ langgraph-graph-api-nodes-execution-info-ids-js validated");
// :remove-end:
