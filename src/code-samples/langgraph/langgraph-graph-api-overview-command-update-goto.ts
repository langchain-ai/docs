// :remove-start:
import { END, START, StateGraph, StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({ foo: z.string() });

const graph = new StateGraph(State)
  .addNode("myOtherNode", (state) => ({ foo: `${state.foo}!` }))
  .addEdge(START, "myNode")
  .addEdge("myOtherNode", END);
// :remove-end:
// :snippet-start: langgraph-graph-api-overview-command-update-goto-js
import { Command } from "@langchain/langgraph";

graph.addNode("myNode", (state) => {
  return new Command({
    update: { foo: "bar" },
    goto: "myOtherNode",
  });
}, {
  ends: ["myOtherNode", END],
});
// :snippet-end:

// :remove-start:
const result = await graph.compile().invoke({ foo: "" });
if (result.foo !== "bar!") {
  throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
}
console.log("✓ langgraph-graph-api-overview-command-update-goto-js");
// :remove-end:
