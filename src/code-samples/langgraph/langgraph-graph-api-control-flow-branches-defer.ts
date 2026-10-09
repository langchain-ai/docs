// :snippet-start: langgraph-graph-api-control-flow-branches-defer-js
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

const nodeA: GraphNode<typeof State> = (state) => {
  console.log(`Adding "A" to ${state.aggregate}`);
  return { aggregate: ["A"] };
};

const nodeB: GraphNode<typeof State> = (state) => {
  console.log(`Adding "B" to ${state.aggregate}`);
  return { aggregate: ["B"] };
};

const nodeB2: GraphNode<typeof State> = (state) => {
  console.log(`Adding "B_2" to ${state.aggregate}`);
  return { aggregate: ["B_2"] };
};

const nodeC: GraphNode<typeof State> = (state) => {
  console.log(`Adding "C" to ${state.aggregate}`);
  return { aggregate: ["C"] };
};

const nodeD: GraphNode<typeof State> = (state) => {
  console.log(`Adding "D" to ${state.aggregate}`);
  return { aggregate: ["D"] };
};

const graph = new StateGraph(State)
  .addNode("a", nodeA)
  .addNode("b", nodeB)
  .addNode("b_2", nodeB2)
  .addNode("c", nodeC)
  .addNode("d", nodeD, { defer: true }) // [!code highlight]
  .addEdge(START, "a")
  .addEdge("a", "b")
  .addEdge("a", "c")
  .addEdge("b", "b_2")
  .addEdge("b_2", "d")
  .addEdge("c", "d")
  .addEdge("d", END)
  .compile();
// :snippet-end:

// :snippet-start: langgraph-graph-api-control-flow-branches-defer-invoke-js
const result = await graph.invoke({ aggregate: [] });
console.log(result);
// :snippet-end:

// :remove-start:
const aggregate = result.aggregate;
if (
  aggregate.length !== 5 ||
  aggregate[0] !== "A" ||
  [...aggregate.slice(1, 3)].sort().join() !== "B,C" ||
  aggregate.slice(3).join() !== "B_2,D"
) {
  throw new Error(`Unexpected aggregate: ${JSON.stringify(aggregate)}`);
}
console.log("✓ langgraph-graph-api-control-flow-branches-defer-js");
// :remove-end:
