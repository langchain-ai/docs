// :snippet-start: langgraph-graph-api-overview-state-fields-js
import {
  StateSchema,
  ReducedValue,
  MessagesValue,
  UntrackedValue,
} from "@langchain/langgraph";
import * as z from "zod";

const AgentState = new StateSchema({
  messages: MessagesValue,
  currentStep: z.string(),
  retryCount: z.number().default(0),
  allSteps: new ReducedValue(
    z.array(z.string()).default(() => []),
    {
      inputSchema: z.string(),
      reducer: (current, newStep) => [...current, newStep],
    }
  ),
  tempCache: new UntrackedValue(z.record(z.string(), z.unknown())),
});
// :snippet-end:

// :remove-start:
import { END, START, StateGraph } from "@langchain/langgraph";

const graph = new StateGraph(AgentState)
  .addNode("step", () => ({ currentStep: "done", allSteps: "second" }))
  .addEdge(START, "step")
  .addEdge("step", END)
  .compile();

const result = await graph.invoke({
  messages: [],
  currentStep: "start",
  allSteps: "first",
  tempCache: {},
});
if (
  result.currentStep !== "done" ||
  result.retryCount !== 0 ||
  JSON.stringify(result.allSteps) !== JSON.stringify(["first", "second"])
) {
  throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
}
console.log("✓ langgraph-graph-api-overview-state-fields-js");
// :remove-end:
