// :snippet-start: langgraph-graph-api-state-define-js
import { StateSchema, MessagesValue } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  messages: MessagesValue,
  extraField: z.number(),
});
// :snippet-end:

// :snippet-start: langgraph-graph-api-state-update-node-js
import { AIMessage } from "@langchain/core/messages";
import { GraphNode } from "@langchain/langgraph";

const node: GraphNode<typeof State> = (state) => {
  const newMessage = new AIMessage("Hello!");
  return { messages: [newMessage], extraField: 10 };
};
// :snippet-end:

// :snippet-start: langgraph-graph-api-state-build-graph-js
import { StateGraph } from "@langchain/langgraph";

const graph = new StateGraph(State)
  .addNode("node", node)
  .addEdge("__start__", "node")
  .compile();
// :snippet-end:

// :snippet-start: langgraph-graph-api-state-invoke-js
import { HumanMessage } from "@langchain/core/messages";

const result = await graph.invoke({
  messages: [new HumanMessage("Hi")],
  extraField: 0,
});
console.log(result);
// :snippet-end:

// :snippet-start: langgraph-graph-api-state-inspect-js
for (const message of result.messages) {
  console.log(`${message.getType()}: ${message.content}`);
}
// :snippet-end:

// :remove-start:
async function main() {
  const types = result.messages.map((m) => m.getType());
  const contents = result.messages.map((m) => m.content);
  if (
    JSON.stringify(types) !== JSON.stringify(["human", "ai"]) ||
    JSON.stringify(contents) !== JSON.stringify(["Hi", "Hello!"])
  ) {
    throw new Error(`Unexpected messages: ${JSON.stringify(result.messages)}`);
  }
  if (result.extraField !== 10) {
    throw new Error(`Unexpected extraField: ${result.extraField}`);
  }
  console.log("✓ langgraph-graph-api-state-define-update-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
