// :remove-start:
import { AIMessage, HumanMessage } from "@langchain/core/messages";
import { StateGraph } from "@langchain/langgraph";
// :remove-end:

// :snippet-start: langgraph-graph-api-state-reducer-define-js
import { StateSchema, MessagesValue } from "@langchain/langgraph";
import * as z from "zod";

// MessagesValue already has a built-in reducer
const State = new StateSchema({
  messages: MessagesValue, // [!code highlight]
  extraField: z.number(),
});
// :snippet-end:

// :snippet-start: langgraph-graph-api-state-reducer-node-js
import { GraphNode } from "@langchain/langgraph";

const node: GraphNode<typeof State> = (state) => {
  const newMessage = new AIMessage("Hello!");
  return { messages: [newMessage], extraField: 10 }; // [!code highlight]
};
// :snippet-end:

// :snippet-start: langgraph-graph-api-state-reducer-invoke-js
import { START } from "@langchain/langgraph";

const graph = new StateGraph(State)
  .addNode("node", node)
  .addEdge(START, "node")
  .compile();

const result = await graph.invoke({ messages: [new HumanMessage("Hi")] });

for (const message of result.messages) {
  console.log(`${message.getType()}: ${message.content}`);
}
// :snippet-end:

// :remove-start:
async function main() {
  const contents = result.messages.map((m) => m.content);
  if (JSON.stringify(contents) !== JSON.stringify(["Hi", "Hello!"])) {
    throw new Error(`Unexpected messages: ${JSON.stringify(result.messages)}`);
  }
  console.log("✓ langgraph-graph-api-state-reducer-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
