// :remove-start:
import {
  END,
  START,
  StateGraph,
  StateSchema,
  ReducedValue,
  GraphNode,
  ConditionalEdgeRouter,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  aggregate: new ReducedValue(z.array(z.string()).default(() => []), {
    reducer: (x, y) => x.concat(y),
  }),
});

const nodeA: GraphNode<typeof State> = () => ({ aggregate: ["A"] });
const nodeB: GraphNode<typeof State> = () => ({ aggregate: ["B"] });

const terminationCondition = (state: typeof State.State) =>
  state.aggregate.length >= 7;
// :remove-end:

// :snippet-start: langgraph-graph-api-control-flow-loops-termination-js
const route: ConditionalEdgeRouter<{ InputSchema: typeof State; Nodes: "b" }> = (state) => {
  if (terminationCondition(state)) {
    return END;
  } else {
    return "b";
  }
};

const graph = new StateGraph(State)
  .addNode("a", nodeA)
  .addNode("b", nodeB)
  .addEdge(START, "a")
  .addConditionalEdges("a", route)
  .addEdge("b", "a")
  .compile();
// :snippet-end:

// :remove-start:
const result = await graph.invoke({ aggregate: [] });
if (result.aggregate.join("") !== "ABABABA") {
  throw new Error(`Unexpected aggregate: ${JSON.stringify(result.aggregate)}`);
}
console.log("✓ langgraph-graph-api-control-flow-loops-termination-js");
// :remove-end:
