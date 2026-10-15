// :snippet-start: langgraph-interrupts-validate-conditional-edge-js
import {
  Command,
  MemorySaver,
  START,
  END,
  StateGraph,
  StateSchema,
  interrupt,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  age: z.number().nullable(),
  pendingQuestion: z.string().nullable(),
});

const builder = new StateGraph(State)
  .addNode("collectAge", (state) => {
    const question = state.pendingQuestion ?? "What is your age?";
    const answer = interrupt(question); // called exactly once per invocation

    if (typeof answer === "number" && answer > 0) {
      return { age: answer, pendingQuestion: null };
    }
    return {
      pendingQuestion: `'${answer}' is not a valid age. Please enter a positive number.`,
    };
  })
  .addEdge(START, "collectAge")
  .addConditionalEdges("collectAge", (state) =>
    state.age !== null ? END : "collectAge",
  );

const checkpointer = new MemorySaver();
const graph = builder.compile({ checkpointer });

const config = { configurable: { thread_id: "form-1" } };
const first = await graph.invoke({ age: null, pendingQuestion: null }, config);
console.log(first.__interrupt__); // -> [{ value: "What is your age?", ... }]

// Provide invalid data; the node re-prompts via the conditional edge
const retry = await graph.invoke(new Command({ resume: "thirty" }), config);
console.log(retry.__interrupt__); // -> [{ value: "'thirty' is not a valid age...", ... }]

// Provide valid data; route returns END and the graph finishes
const final = await graph.invoke(new Command({ resume: 30 }), config);
console.log(final.age); // -> 30
// :snippet-end:

// :remove-start:
if (!first.__interrupt__?.length) {
  throw new Error("Expected interrupt on first invoke");
}
if (!retry.__interrupt__?.length) {
  throw new Error("Expected interrupt on retry");
}
if (final.age !== 30) {
  throw new Error(`Expected age=30, got ${final.age}`);
}
console.log("✓ langgraph-interrupts-validate-conditional-edge");
// :remove-end:
