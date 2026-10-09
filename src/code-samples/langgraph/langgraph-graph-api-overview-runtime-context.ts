// :snippet-start: langgraph-graph-api-overview-runtime-context-js
import { END, START, StateGraph, StateSchema, GraphNode } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  input: z.string(),
  output: z.string(),
});

const ContextSchema = z.object({
  llm: z.union([z.literal("openai"), z.literal("anthropic")]),
});

const getLLM = (provider?: string) => provider;

const nodeA: GraphNode<typeof State> = (state, config) => {
  const llm = getLLM(config.context?.llm);
  return { output: llm ?? "" };
};

const graph = new StateGraph(State, ContextSchema)
  .addNode("nodeA", nodeA)
  .addEdge(START, "nodeA")
  .addEdge("nodeA", END)
  .compile();

const inputs = { input: "hi" };
await graph.invoke(inputs, { context: { llm: "anthropic" } });
// :snippet-end:

// :remove-start:
const result = await graph.invoke(inputs, { context: { llm: "anthropic" } });
if (result.output !== "anthropic") {
  throw new Error(`Expected output "anthropic", got ${JSON.stringify(result)}`);
}
console.log("✓ langgraph-graph-api-overview-runtime-context-js");
// :remove-end:
