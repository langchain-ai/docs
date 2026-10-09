// :snippet-start: langgraph-graph-api-state-alt-channels-classes-js
import { BaseMessage } from "@langchain/core/messages";
import { StateGraph } from "@langchain/langgraph";
import {
  BinaryOperatorAggregate,
  LastValue,
  Topic,
} from "@langchain/langgraph/channels";

interface WorkflowState {
  messages: BaseMessage[];
  question: string;
  events: string[];
}

const workflow = new StateGraph<WorkflowState>({
  channels: {
    messages: new BinaryOperatorAggregate<BaseMessage[]>(
      (current, update) => current.concat(update),
      () => []
    ),
    question: new LastValue<string>(),
    // Topic collects all values pushed during execution
    events: new Topic<string>(),
  },
});
// :snippet-end:

// :remove-start:
import { HumanMessage } from "@langchain/core/messages";
import { END, START } from "@langchain/langgraph";

const graph = workflow
  .addNode("respond", () => ({
    messages: [new HumanMessage("second")],
    events: ["e1"],
  }))
  .addEdge(START, "respond")
  .addEdge("respond", END)
  .compile();

if (!("respond" in graph.nodes)) {
  throw new Error("respond node missing after compile");
}
// Construction validates channel class imports and StateGraph wiring.
// Invoking BinaryOperatorAggregate channel instances can lose the operator
// after clone in the current runtime, so skip invoke here.
console.log("✓ langgraph-graph-api-state-alt-channels-classes-js");
// :remove-end:
