// :snippet-start: langgraph-graph-api-reducers-replace-js
import { ReducedValue, StateSchema } from "@langchain/langgraph";
import { z } from "zod/v4";

const State = new StateSchema({
  errors: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (_state: string[], update: string[]) => update }
  ),
});

// node can now clear the field with { errors: [] }
// :snippet-end:

// :remove-start:
import { END, START, StateGraph } from "@langchain/langgraph";

const graph = new StateGraph(State)
  .addNode("recordError", () => ({ errors: ["bad sql"] }))
  .addNode("clearErrors", () => ({ errors: [] }))
  .addEdge(START, "recordError")
  .addEdge("recordError", "clearErrors")
  .addEdge("clearErrors", END)
  .compile();

async function main() {
  const result = await graph.invoke({ errors: [] });
  if (JSON.stringify(result.errors) !== JSON.stringify([])) {
    throw new Error(
      `Expected replace reducer to clear errors, got: ${JSON.stringify(result.errors)}`
    );
  }
  console.log("✓ langgraph-graph-api-reducers-replace-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
