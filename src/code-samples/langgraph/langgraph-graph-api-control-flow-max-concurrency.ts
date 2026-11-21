// :remove-start:
import {
  START,
  StateGraph,
  StateSchema,
  GraphNode,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  value1: z.string(),
  value2: z.number(),
});

const step1: GraphNode<typeof State> = (state) => ({ value1: "a" });
const step2: GraphNode<typeof State> = (state) => ({
  value1: `${state.value1} b`,
});
const step3: GraphNode<typeof State> = (state) => ({ value2: 10 });

const graph = new StateGraph(State)
  .addNode("step1", step1)
  .addNode("step2", step2)
  .addNode("step3", step3)
  .addEdge(START, "step1")
  .addEdge("step1", "step2")
  .addEdge("step2", "step3")
  .compile();
// :remove-end:

// :snippet-start: langgraph-graph-api-control-flow-max-concurrency-js
const result = await graph.invoke({ value1: "c" }, { maxConcurrency: 10 });
// :snippet-end:

// :remove-start:
if (result.value1 !== "a b" || result.value2 !== 10) {
  throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
}
console.log("✓ langgraph-graph-api-control-flow-max-concurrency-js");
// :remove-end:
