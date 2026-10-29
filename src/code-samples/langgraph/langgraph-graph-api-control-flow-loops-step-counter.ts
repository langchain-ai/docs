// :snippet-start: langgraph-graph-api-control-flow-loops-step-counter-js
import type { LangGraphRunnableConfig } from "@langchain/langgraph";

const myNode = (
  state: Record<string, unknown>,
  config: LangGraphRunnableConfig
) => {
  const currentStep = config.metadata?.langgraph_step;
  console.log(`Currently on step: ${currentStep}`);
  return state;
};
// :snippet-end:

// :remove-start:
import { END, START, StateGraph, StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({ value: z.string() });

const graph = new StateGraph(State)
  .addNode("myNode", myNode)
  .addEdge(START, "myNode")
  .addEdge("myNode", END)
  .compile();

const result = await graph.invoke({ value: "x" });
if (result.value !== "x") {
  throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
}
console.log("✓ langgraph-graph-api-control-flow-loops-step-counter-js");
// :remove-end:
