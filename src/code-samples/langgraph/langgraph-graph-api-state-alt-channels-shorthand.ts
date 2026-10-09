// :snippet-start: langgraph-graph-api-state-alt-channels-shorthand-js
import { BaseMessage } from "@langchain/core/messages";
import { StateGraph } from "@langchain/langgraph";

interface WorkflowState {
  messages: BaseMessage[];
  question: string;
  answer: string;
}

const workflow = new StateGraph<WorkflowState>({
  channels: {
    // BinaryOperatorAggregate: combines values with a reducer
    messages: {
      reducer: (current, update) => current.concat(update),
      default: () => [],
    },
    // LastValue: stores the most recent value (null = no reducer)
    question: null,
    answer: null,
  },
});
// :snippet-end:

// :remove-start:
import { HumanMessage } from "@langchain/core/messages";
import { END, START } from "@langchain/langgraph";

const graph = workflow
  .addNode("respond", () => ({
    messages: [new HumanMessage("second")],
    answer: "done",
  }))
  .addEdge(START, "respond")
  .addEdge("respond", END)
  .compile();

async function main() {
  const result = await graph.invoke({
    messages: [new HumanMessage("first")],
    question: "q",
  });
  const contents = result.messages.map((m) => m.content);
  if (JSON.stringify(contents) !== JSON.stringify(["first", "second"])) {
    throw new Error(`Reducer channel did not merge: ${JSON.stringify(contents)}`);
  }
  if (result.question !== "q" || result.answer !== "done") {
    throw new Error(`Unexpected state: ${JSON.stringify(result)}`);
  }
  console.log("✓ langgraph-graph-api-state-alt-channels-shorthand-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
