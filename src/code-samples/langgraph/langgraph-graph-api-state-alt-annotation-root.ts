// :snippet-start: langgraph-graph-api-state-alt-annotation-root-js
import { BaseMessage } from "@langchain/core/messages";
import { Annotation, StateGraph, messagesStateReducer } from "@langchain/langgraph";

const State = Annotation.Root({
  messages: Annotation<BaseMessage[]>({
    reducer: messagesStateReducer,
    default: () => [],
  }),
  question: Annotation<string>(),
  count: Annotation<number>({
    reducer: (current, update) => current + update,
    default: () => 0,
  }),
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
  console.log("✓ langgraph-graph-api-state-alt-annotation-root-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
