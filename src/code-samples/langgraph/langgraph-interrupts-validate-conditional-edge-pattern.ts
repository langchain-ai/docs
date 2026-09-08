// :remove-start:
import {
  Command,
  END,
  MemorySaver,
  START,
  StateGraph,
  StateSchema,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  age: z.number().nullable(),
  pendingQuestion: z.string().nullable(),
});
// :remove-end:

// :snippet-start: langgraph-interrupts-validate-conditional-edge-pattern-js
import { interrupt } from "@langchain/langgraph";

const getAgeNode: typeof State.Node = (state) => {
  const question = state.pendingQuestion ?? "What is your age?";
  const answer = interrupt(question); // called exactly once per invocation

  if (typeof answer === "number" && answer > 0) {
    return { age: answer, pendingQuestion: null };
  }
  return {
    pendingQuestion: `'${answer}' is not a valid age. Please enter a positive number.`,
  };
};

// builder.addConditionalEdges("collectAge", (state) =>
//   state.age !== null ? END : "collectAge"
// );
// :snippet-end:

// :remove-start:
const builder = new StateGraph(State)
  .addNode("collectAge", getAgeNode)
  .addEdge(START, "collectAge")
  .addConditionalEdges("collectAge", (state) =>
    state.age !== null ? END : "collectAge",
  );

const graph = builder.compile({ checkpointer: new MemorySaver() });

async function main() {
  const config = { configurable: { thread_id: "form-pattern-test" } };
  const first = await graph.invoke(
    { age: null, pendingQuestion: null },
    config,
  );
  if (!first.__interrupt__?.length) {
    throw new Error("Expected interrupt on first invoke");
  }

  const retry = await graph.invoke(new Command({ resume: "thirty" }), config);
  if (!retry.__interrupt__?.length) {
    throw new Error("Expected interrupt on retry");
  }

  const final = await graph.invoke(new Command({ resume: 30 }), config);
  if (final.age !== 30) {
    throw new Error(`Expected age=30, got ${final.age}`);
  }
  console.log("✓ langgraph-interrupts-validate-conditional-edge-pattern");
}

main();
// :remove-end:
