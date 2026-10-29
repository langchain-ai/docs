// :snippet-start: langgraph-graph-api-state-alt-zod-v4-js
import * as z from "zod";
import { BaseMessage } from "@langchain/core/messages";
import { StateGraph, MessagesZodMeta, messagesStateReducer } from "@langchain/langgraph";
import { registry } from "@langchain/langgraph/zod";

const State = z.object({
  // Use .register() with the LangGraph registry and MessagesZodMeta
  messages: z
    .array(z.custom<BaseMessage>())
    .default([])
    .register(registry, MessagesZodMeta),
  // Simple fields work directly (last-write-wins)
  question: z.string().optional(),
  answer: z.string().optional(),
  // Custom reducer via registry metadata
  count: z
    .number()
    .default(0)
    .register(registry, {
      reducer: { fn: (current: number, update: number) => current + update },
    }),
});

const graph = new StateGraph(State);
// :snippet-end:

// :remove-start:
import { HumanMessage } from "@langchain/core/messages";
import { END, START } from "@langchain/langgraph";

// messagesStateReducer is imported in the docs snippet for parity with the
// Zod v3 example; reference it so the import is exercised.
if (typeof messagesStateReducer !== "function") {
  throw new Error("messagesStateReducer is not exported");
}

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
  console.log("✓ langgraph-graph-api-state-alt-zod-v4-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
