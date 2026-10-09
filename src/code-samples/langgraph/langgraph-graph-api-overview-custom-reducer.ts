// :snippet-start: langgraph-graph-api-overview-custom-reducer-js
import { StateSchema, ReducedValue } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  foo: z.number(),
  bar: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (left, right) => left.concat(right) }
  ),
});
// :snippet-end:

// :remove-start:
import { END, START, StateGraph } from "@langchain/langgraph";

const graph = new StateGraph(State)
  .addNode("update", () => ({ bar: ["bye"] }))
  .addEdge(START, "update")
  .addEdge("update", END)
  .compile();

const result = await graph.invoke({ foo: 1, bar: ["hi"] });
if (
  result.foo !== 1 ||
  JSON.stringify(result.bar) !== JSON.stringify(["hi", "bye"])
) {
  throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
}
console.log("✓ langgraph-graph-api-overview-custom-reducer-js");
// :remove-end:
