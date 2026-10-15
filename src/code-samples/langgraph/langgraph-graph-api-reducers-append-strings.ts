// :snippet-start: langgraph-graph-api-reducers-append-strings-js
import { ReducedValue, StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  tags: new ReducedValue(
    z.array(z.string()).default(() => []),
    {
      reducer: (left: string[], right: string[]) => {
        // left: existing state; right: update from a node
        return left.concat(right);
      },
    }
  ),
});
// :snippet-end:

// :remove-start:
import { END, START, StateGraph } from "@langchain/langgraph";

const graph = new StateGraph(State)
  .addNode("appendTag", () => ({ tags: ["review"] }))
  .addEdge(START, "appendTag")
  .addEdge("appendTag", END)
  .compile();

async function main() {
  const result = await graph.invoke({ tags: ["draft"] });
  if (JSON.stringify(result.tags) !== JSON.stringify(["draft", "review"])) {
    throw new Error(`Unexpected tags: ${JSON.stringify(result.tags)}`);
  }
  console.log("✓ langgraph-graph-api-reducers-append-strings-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
