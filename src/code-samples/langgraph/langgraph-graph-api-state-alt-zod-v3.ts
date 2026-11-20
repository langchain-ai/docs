// :snippet-start: langgraph-graph-api-state-alt-zod-v3-js
import { z } from "zod/v3";
import { BaseMessage } from "@langchain/core/messages";
import { StateGraph, messagesStateReducer } from "@langchain/langgraph";
import "@langchain/langgraph/zod"; // registers the .langgraph plugin on Zod schemas

const State = z.object({
  // Use .langgraph.reducer() to attach a reducer function
  messages: z
    .array(z.custom<BaseMessage>())
    .default([])
    .langgraph.reducer(messagesStateReducer),
  // Simple fields work directly (last-write-wins)
  question: z.string().optional(),
  answer: z.string().optional(),
  // Custom reducer for accumulating values
  count: z
    .number()
    .default(0)
    .langgraph.reducer((current, update) => current + update),
});

const graph = new StateGraph(State);
// :snippet-end:

// :remove-start:
import { HumanMessage } from "@langchain/core/messages";
import { END, START } from "@langchain/langgraph";

const compiled = graph
  .addNode("step", () => ({
    messages: [new HumanMessage("second")],
    count: 2,
  }))
  .addEdge(START, "step")
  .addEdge("step", END)
  .compile();

async function main() {
  const result = await compiled.invoke({
    messages: [new HumanMessage("first")],
    question: "q",
    count: 1,
  });
  const contents = result.messages.map((m) => m.content);
  if (JSON.stringify(contents) !== JSON.stringify(["first", "second"])) {
    throw new Error(`Unexpected messages: ${JSON.stringify(contents)}`);
  }
  if (result.count !== 3 || result.question !== "q") {
    throw new Error(`Unexpected state: ${JSON.stringify(result)}`);
  }
  console.log("✓ langgraph-graph-api-state-alt-zod-v3-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
