// :snippet-start: langgraph-graph-api-state-input-output-js
import { StateGraph, StateSchema, GraphNode, START, END } from "@langchain/langgraph";
import * as z from "zod";

// Define the schema for the input
const InputState = new StateSchema({
  question: z.string(),
});

// Define the schema for the output
const OutputState = new StateSchema({
  answer: z.string(),
});

// Define the overall schema, combining both input and output
const OverallState = new StateSchema({
  question: z.string(),
  answer: z.string(),
});

// Define the node that processes the input
const answerNode: GraphNode<typeof OverallState> = (state) => {
  // Example answer and an extra key
  return { answer: "bye", question: state.question };
};

// Build the graph with input and output schemas specified
const graph = new StateGraph({
  input: InputState,
  output: OutputState,
  state: OverallState,
})
  .addNode("answerNode", answerNode)
  .addEdge(START, "answerNode")
  .addEdge("answerNode", END)
  .compile();

// Invoke the graph with an input and print the result
console.log(await graph.invoke({ question: "hi" }));
// :snippet-end:

// :remove-start:
async function main() {
  const result = await graph.invoke({ question: "hi" });
  if (JSON.stringify(result) !== JSON.stringify({ answer: "bye" })) {
    throw new Error(`Unexpected output: ${JSON.stringify(result)}`);
  }
  console.log("✓ langgraph-graph-api-state-input-output-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
