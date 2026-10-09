// :snippet-start: langgraph-graph-api-overview-messages-js
import { StateSchema, MessagesValue } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  messages: MessagesValue,
  documents: z.array(z.string()),
});
// :snippet-end:

// :remove-start:
import { END, START, StateGraph } from "@langchain/langgraph";
import { AIMessage, HumanMessage } from "@langchain/core/messages";

const graph = new StateGraph(State)
  .addNode("reply", () => ({ messages: [new AIMessage("hello")] }))
  .addEdge(START, "reply")
  .addEdge("reply", END)
  .compile();

// Both message objects and plain objects deserialize into message objects.
for (const input of [
  new HumanMessage("message"),
  { role: "human", content: "message" },
]) {
  const result = await graph.invoke({ messages: [input], documents: [] });
  if (
    !HumanMessage.isInstance(result.messages[0]) ||
    result.messages[0].content !== "message" ||
    result.messages.at(-1)?.content !== "hello"
  ) {
    throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
  }
}
console.log("✓ langgraph-graph-api-overview-messages-js");
// :remove-end:
