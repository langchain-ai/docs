// :remove-start:
import { AIMessage } from "@langchain/core/messages";
// :remove-end:

// :snippet-start: langgraph-graph-api-state-messages-value-js
import { StateSchema, StateGraph, MessagesValue, GraphNode, START } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({ // [!code highlight]
  messages: MessagesValue,
  extraField: z.number(),
});

const node: GraphNode<typeof State> = (state) => {
  const newMessage = new AIMessage("Hello!");
  return { messages: [newMessage], extraField: 10 };
};

const graph = new StateGraph(State)
  .addNode("node", node)
  .addEdge(START, "node")
  .compile();
// :snippet-end:

// :snippet-start: langgraph-graph-api-state-messages-value-invoke-js
const inputMessage = { role: "user", content: "Hi" }; // [!code highlight]

const result = await graph.invoke({ messages: [inputMessage] });

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
  console.log("✓ langgraph-graph-api-state-messages-value-js");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// :remove-end:
