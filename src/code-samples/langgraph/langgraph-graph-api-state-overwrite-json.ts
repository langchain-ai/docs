// :snippet-start: langgraph-graph-api-state-overwrite-json-js
const replaceMessages = () => {
  return { messages: { __overwrite__: ["replacement message"] } };
};
// :snippet-end:

// :remove-start:
import {
  END,
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

const graph = new StateGraph(State)
  .addNode("add_message", () => ({ messages: ["first message"] }))
  .addNode("replace_messages", replaceMessages)
  .addEdge(START, "add_message")
  .addEdge("add_message", "replace_messages")
  .addEdge("replace_messages", END)
  .compile();

async function main() {
  const result = await graph.invoke({ messages: ["initial"] });
  if (JSON.stringify(result.messages) !== JSON.stringify(["replacement message"])) {
    throw new Error(`Unexpected messages: ${JSON.stringify(result.messages)}`);
  }
  console.log("✓ langgraph-graph-api-state-overwrite-json-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
