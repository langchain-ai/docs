// :snippet-start: langgraph-graph-api-nodes-cache-js
import { StateGraph, StateSchema, GraphNode, START, END } from "@langchain/langgraph";
import { InMemoryCache } from "@langchain/langgraph-checkpoint";
import * as z from "zod";

const State = new StateSchema({
  x: z.number(),
  result: z.number(),
});

const expensiveNode: GraphNode<typeof State> = async (state) => {
  // Simulate an expensive operation
  await new Promise((resolve) => setTimeout(resolve, 3000));
  return { result: state.x * 2 };
};

const graph = new StateGraph(State)
  .addNode("expensive_node", expensiveNode, { cachePolicy: { ttl: 3 } })
  .addEdge(START, "expensive_node")
  .addEdge("expensive_node", END)
  .compile({ cache: new InMemoryCache() });

await graph.invoke({ x: 5 }, { streamMode: "updates" });  // [!code highlight]
// [{"expensive_node": {"result": 10}}]
await graph.invoke({ x: 5 }, { streamMode: "updates" });  // [!code highlight]
// [{"expensive_node": {"result": 10}, "__metadata__": {"cached": true}}]
// :snippet-end:

// :remove-start:
const cached = await graph.invoke({ x: 5 }, { streamMode: "updates" });
const expected = [
  { expensive_node: { result: 10 }, __metadata__: { cached: true } },
];
if (JSON.stringify(cached) !== JSON.stringify(expected)) {
  throw new Error(`Expected a cache hit, got: ${JSON.stringify(cached)}`);
}
console.log("✓ langgraph-graph-api-nodes-cache-js validated");
// :remove-end:
