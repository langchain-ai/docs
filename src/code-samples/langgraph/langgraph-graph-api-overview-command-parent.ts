// :remove-start:
import { END, START, StateGraph, StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const Schema = new StateSchema({ foo: z.string() });
type State = typeof Schema.State;
// :remove-end:
// :snippet-start: langgraph-graph-api-overview-command-parent-js
import { Command } from "@langchain/langgraph";

const myNode = (state: State): Command => {
  return new Command({
    update: { foo: "bar" },
    goto: "otherSubgraph",  // where `otherSubgraph` is a node in the parent graph
    graph: Command.PARENT,
  });
};
// :snippet-end:

// :remove-start:
const subgraph = new StateGraph(Schema)
  .addNode("myNode", myNode)
  .addEdge(START, "myNode")
  .compile();

const parentGraph = new StateGraph(Schema)
  .addNode("subgraphNode", subgraph, { ends: ["otherSubgraph"] })
  .addNode("otherSubgraph", (state) => ({ foo: `${state.foo}!` }))
  .addEdge(START, "subgraphNode")
  .addEdge("otherSubgraph", END)
  .compile();

const result = await parentGraph.invoke({ foo: "" });
if (result.foo !== "bar!") {
  throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
}
console.log("✓ langgraph-graph-api-overview-command-parent-js");
// :remove-end:
