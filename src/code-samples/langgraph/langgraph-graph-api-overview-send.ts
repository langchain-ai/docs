// :remove-start:
import { END, START, StateGraph, StateSchema, ReducedValue } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  subjects: z.array(z.string()),
  jokes: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (left, right) => left.concat(right) }
  ),
});

const graph = new StateGraph(State)
  .addNode("nodeA", (state) => ({ subjects: state.subjects }))
  .addNode("generateJoke", (state: { subject: string }) => ({
    jokes: [`A joke about ${state.subject}`],
  }))
  .addEdge(START, "nodeA")
  .addEdge("generateJoke", END);
// :remove-end:
// :snippet-start: langgraph-graph-api-overview-send-js
import { Send } from "@langchain/langgraph";

graph.addConditionalEdges("nodeA", (state) => {
  return state.subjects.map(
    (subject) => new Send("generateJoke", { subject })
  );
});
// :snippet-end:

// :remove-start:
const result = await graph.compile().invoke({ subjects: ["cats", "dogs"], jokes: [] });
if (
  JSON.stringify([...result.jokes].sort()) !==
  JSON.stringify(["A joke about cats", "A joke about dogs"])
) {
  throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
}
console.log("✓ langgraph-graph-api-overview-send-js");
// :remove-end:
