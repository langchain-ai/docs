// :snippet-start: langgraph-functional-api-workflows-graph-js
import { entrypoint, MemorySaver, START, StateGraph, StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  foo: z.number(),
});

const builder = new StateGraph(State)
  .addNode("double", (state) => {
    return { foo: state.foo * 2 };
  })
  .addEdge(START, "double");
const graph = builder.compile();

const checkpointer = new MemorySaver();

const workflow = entrypoint(
  { checkpointer, name: "workflow" },
  async (x: number, config) => {
    const result = await graph.invoke({ foo: x }, config);
    return { bar: result.foo };
  }
);

const config = { configurable: { thread_id: crypto.randomUUID() } };
console.log(await workflow.invoke(5, config)); // { bar: 10 }
// :snippet-end:

// :remove-start:
const graphResult = await workflow.invoke(5, {
  configurable: { thread_id: crypto.randomUUID() },
});
if (graphResult.bar !== 10) {
  throw new Error(`expected bar 10, got ${JSON.stringify(graphResult)}`);
}
console.log("✓ langgraph-functional-api-workflows-graph");
// :remove-end:
