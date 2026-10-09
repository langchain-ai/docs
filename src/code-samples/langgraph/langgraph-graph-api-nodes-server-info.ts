// :snippet-start: langgraph-graph-api-nodes-server-info-js
import { StateGraph, StateSchema, GraphNode, START, END } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  result: z.string(),
});

const myNode: GraphNode<typeof State> = async (state, config) => {
  const server = config.serverInfo;
  if (server != null) {
    console.log(`Assistant: ${server.assistantId}, Graph: ${server.graphId}`);  // [!code highlight]
    if (server.user != null) {
      console.log(`User: ${JSON.stringify(server.user)}`);
    }
  }
  return { result: "done" };
};

const graph = new StateGraph(State)
  .addNode("my_node", myNode)
  .addEdge(START, "my_node")
  .addEdge("my_node", END)
  .compile();
// :snippet-end:

// :remove-start:
// `serverInfo` is undefined outside LangGraph Server, so the node skips the logs.
const result = await graph.invoke({ result: "" });
if (result.result !== "done") throw new Error(`Unexpected result: ${result.result}`);
console.log("✓ langgraph-graph-api-nodes-server-info-js validated");
// :remove-end:
