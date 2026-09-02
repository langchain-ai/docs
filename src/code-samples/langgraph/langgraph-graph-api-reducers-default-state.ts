// :snippet-start: langgraph-graph-api-reducers-default-state-js
import { StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  foo: z.number(),
  bar: z.array(z.string()),
});
// :snippet-end:

// :remove-start:
import { END, START, StateGraph } from "@langchain/langgraph";

const graph = new StateGraph(State)
  .addNode("first", () => ({ foo: 2 }))
  .addNode("second", () => ({ bar: ["bye"] }))
  .addEdge(START, "first")
  .addEdge("first", "second")
  .addEdge("second", END)
  .compile();

async function main() {
  const result = await graph.invoke({ foo: 1, bar: ["hi"] });
  if (result.foo !== 2 || JSON.stringify(result.bar) !== JSON.stringify(["bye"])) {
    throw new Error(`Unexpected default reducer result: ${JSON.stringify(result)}`);
  }
  console.log("✓ langgraph-graph-api-reducers-default-state-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
