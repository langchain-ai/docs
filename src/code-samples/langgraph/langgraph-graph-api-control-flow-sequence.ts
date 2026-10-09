// :snippet-start: langgraph-graph-api-control-flow-sequence-state-js
import { StateSchema, GraphNode } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  value1: z.string(),
  value2: z.number(),
});
// :snippet-end:

// :snippet-start: langgraph-graph-api-control-flow-sequence-nodes-js
const step1: GraphNode<typeof State> = (state) => {
  return { value1: "a" };
};

const step2: GraphNode<typeof State> = (state) => {
  const currentValue1 = state.value1;
  return { value1: `${currentValue1} b` };
};

const step3: GraphNode<typeof State> = (state) => {
  return { value2: 10 };
};
// :snippet-end:

// :snippet-start: langgraph-graph-api-control-flow-sequence-graph-js
import { START, StateGraph } from "@langchain/langgraph";

const graph = new StateGraph(State)
  .addNode("step1", step1)
  .addNode("step2", step2)
  .addNode("step3", step3)
  .addEdge(START, "step1")
  .addEdge("step1", "step2")
  .addEdge("step2", "step3")
  .compile();
// :snippet-end:

// :snippet-start: langgraph-graph-api-control-flow-sequence-invoke-js
const result = await graph.invoke({ value1: "c" });
console.log(result);
// :snippet-end:

// :remove-start:
if (result.value1 !== "a b" || result.value2 !== 10) {
  throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
}
console.log("✓ langgraph-graph-api-control-flow-sequence-js");
// :remove-end:
