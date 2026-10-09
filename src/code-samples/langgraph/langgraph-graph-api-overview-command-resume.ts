// :remove-start:
import {
  Command,
  END,
  interrupt,
  MemorySaver,
  START,
  StateGraph,
  StateSchema,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({ answer: z.string() });

const graph = new StateGraph(State)
  .addNode("ask", () => ({ answer: interrupt("Continue?") }))
  .addEdge(START, "ask")
  .addEdge("ask", END)
  .compile({ checkpointer: new MemorySaver() });

const config = { configurable: { thread_id: "overview-resume" } };
const paused = await graph.invoke({ answer: "" }, config);
if (!("__interrupt__" in paused)) {
  throw new Error("Expected the graph to pause at the interrupt");
}
// :remove-end:
// :snippet-start: langgraph-graph-api-overview-command-resume-js
await graph.invoke(new Command({ resume: "yes" }), config);
// :snippet-end:

// :remove-start:
const state = await graph.getState(config);
if (state.values.answer !== "yes") {
  throw new Error(`Unexpected state: ${JSON.stringify(state.values)}`);
}
console.log("✓ langgraph-graph-api-overview-command-resume-js");
// :remove-end:
