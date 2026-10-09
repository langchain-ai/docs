// :remove-start:
import {
  StateGraph,
  StateSchema,
  ReducedValue,
  GraphNode,
  START,
  END,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  aggregate: new ReducedValue(z.array(z.string()).default(() => []), {
    reducer: (x, y) => x.concat(y),
  }),
});

const node =
  (label: string): GraphNode<typeof State> =>
  () => ({ aggregate: [label] });

const graph = new StateGraph(State)
  .addNode("a", node("A"))
  .addNode("b", node("B"))
  .addNode("b_2", node("B_2"))
  .addNode("c", node("C"))
  .addNode("d", node("D"))
  .addEdge(START, "a")
  .addEdge("a", "b")
  .addEdge("a", "c")
  .addEdge("b", "b_2")
  // :remove-end:
  // :snippet-start: langgraph-graph-api-control-flow-branches-defer-list-edge-js
  .addEdge(["b_2", "c"], "d") // d runs once, after both b_2 and c complete
  // :snippet-end:
  // :remove-start:
  .addEdge("d", END)
  .compile();

const result = await graph.invoke({ aggregate: [] });
const aggregate = result.aggregate;
if (
  aggregate.filter((label) => label === "D").length !== 1 ||
  aggregate[aggregate.length - 1] !== "D"
) {
  throw new Error(`Unexpected aggregate: ${JSON.stringify(aggregate)}`);
}
console.log("✓ langgraph-graph-api-control-flow-branches-defer-list-edge-js");
// :remove-end:
