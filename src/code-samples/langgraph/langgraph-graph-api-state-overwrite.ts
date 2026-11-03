// :snippet-start: langgraph-graph-api-state-overwrite-js
import {
  END,
  Overwrite,
  ReducedValue,
  START,
  StateGraph,
  StateSchema,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  messages: new ReducedValue(
    z.array(z.string()).default(() => []),
    {
      reducer: (current: string[], update: string[]) => current.concat(update),
    },
  ),
});

const addMessage = () => {
  return { messages: ["first message"] };
};

const replaceMessages = () => {
  // Bypass the reducer and replace the entire messages list
  return { messages: new Overwrite(["replacement message"]) };
};

const graph = new StateGraph(State)
  .addNode("add_message", addMessage)
  .addNode("replace_messages", replaceMessages)
  .addEdge(START, "add_message")
  .addEdge("add_message", "replace_messages")
  .addEdge("replace_messages", END)
  .compile();

const result = await graph.invoke({ messages: ["initial"] });
console.log(result.messages);
// :snippet-end:

// :remove-start:
async function main() {
  if (JSON.stringify(result.messages) !== JSON.stringify(["replacement message"])) {
    throw new Error(`Unexpected messages: ${JSON.stringify(result.messages)}`);
  }
  console.log("✓ langgraph-graph-api-state-overwrite-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
