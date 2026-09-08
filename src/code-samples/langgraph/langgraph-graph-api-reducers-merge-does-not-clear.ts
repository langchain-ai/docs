// :snippet-start: langgraph-graph-api-reducers-merge-does-not-clear-js
import { ReducedValue, StateSchema } from "@langchain/langgraph";
import { z } from "zod/v4";

const State = new StateSchema({
  errors: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (state: string[], update: string[]) => state.concat(update) },
  ),
});

// node A returns { errors: ["bad sql"] }
// node B returns { errors: [] }
// state.errors is still ["bad sql"]; the empty array is merged in, not cleared
// :snippet-end:

// :remove-start:
import { END, START, StateGraph } from "@langchain/langgraph";

const graph = new StateGraph(State)
  .addNode("recordError", () => ({ errors: ["bad sql"] }))
  .addNode("attemptClear", () => ({ errors: [] }))
  .addEdge(START, "recordError")
  .addEdge("recordError", "attemptClear")
  .addEdge("attemptClear", END)
  .compile();

async function main() {
  const result = await graph.invoke({ errors: [] });
  if (JSON.stringify(result.errors) !== JSON.stringify(["bad sql"])) {
    throw new Error(
      `Expected merge to keep errors, got: ${JSON.stringify(result.errors)}`,
    );
  }
  console.log("✓ langgraph-graph-api-reducers-merge-does-not-clear-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
