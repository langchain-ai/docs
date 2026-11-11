// :snippet-start: langgraph-graph-api-visualize-graph-js
import {
  ConditionalEdgeRouter,
  END,
  GraphNode,
  START,
  StateGraph,
  StateSchema,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  value: z.number(),
});

const node1: GraphNode<typeof State> = (state) => {
  return { value: state.value + 1 };
};

const node2: GraphNode<typeof State> = (state) => {
  return { value: state.value * 2 };
};

const router: ConditionalEdgeRouter<{ InputSchema: typeof State; Nodes: "node2" }> = (state) => {
  if (state.value < 10) {
    return "node2";
  }
  return END;
};

const app = new StateGraph(State)
  .addNode("node1", node1)
  .addNode("node2", node2)
  .addEdge(START, "node1")
  .addConditionalEdges("node1", router)
  .addEdge("node2", "node1")
  .compile();
// :snippet-end:

// :remove-start:
// Deterministic: 1 -> node1 (2) -> node2 (4) -> node1 (5) -> node2 (10) -> node1 (11) -> end
const visualizeResult = await app.invoke({ value: 1 });
if (visualizeResult.value !== 11) {
  throw new Error(`expected value 11, got ${visualizeResult.value}`);
}
console.log("✓ langgraph-graph-api-visualize-graph-js validated");
// :remove-end:

// :snippet-start: langgraph-graph-api-visualize-mermaid-js
const drawableGraph = await app.getGraphAsync();
console.log(drawableGraph.drawMermaid());
// :snippet-end:

// :remove-start:
const mermaid = drawableGraph.drawMermaid();
if (!mermaid.includes("__start__")) {
  throw new Error(`expected __start__ in Mermaid output, got ${mermaid}`);
}
if (!mermaid.includes("node1 -.-> node2;")) {
  throw new Error(`expected conditional edge in Mermaid output, got ${mermaid}`);
}
// The Mermaid.ink PNG block stays inline in the docs because it needs network access.
console.log("✓ langgraph-graph-api-visualize-mermaid-js validated");
// :remove-end:
