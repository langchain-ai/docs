// :snippet-start: langgraph-use-graph-api-control-flow-js
import {
  END,
  START,
  StateGraph,
  StateSchema,
  type GraphNode,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  number: z.number(),
  isEven: z.boolean().optional(),
  message: z.string().optional(),
});

const checkEven: GraphNode<typeof State> = (state) => ({
  isEven: state.number % 2 === 0,
});

const formatMessage: GraphNode<typeof State> = (state) => ({
  message: state.isEven ? "The number is even." : "The number is odd.",
});

const graph = new StateGraph(State)
  .addNode("checkEven", checkEven)
  .addNode("formatMessage", formatMessage)
  .addEdge(START, "checkEven")
  .addEdge("checkEven", "formatMessage")
  .addEdge("formatMessage", END)
  .compile();

await graph.invoke({ number: 7 });
// :snippet-end:

// :remove-start:
const oddResult = await graph.invoke({ number: 7 });
if (oddResult.message !== "The number is odd.") {
  throw new Error(`expected odd message, got ${oddResult.message}`);
}
const evenResult = await graph.invoke({ number: 4 });
if (evenResult.message !== "The number is even.") {
  throw new Error(`expected even message, got ${evenResult.message}`);
}
console.log("✓ langgraph-use-graph-api-control-flow-js validated");
// :remove-end:

// :snippet-start: langgraph-use-graph-api-visualize-js
const drawableGraph = await graph.getGraphAsync();
console.log(drawableGraph.drawMermaid());
// :snippet-end:

// :remove-start:
if (!drawableGraph.drawMermaid().includes("__start__")) {
  throw new Error("expected __start__ in Mermaid output");
}
console.log("✓ langgraph-use-graph-api-visualize-js validated");
// :remove-end:
