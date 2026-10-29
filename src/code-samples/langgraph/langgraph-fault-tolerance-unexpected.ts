// :snippet-start: langgraph-fault-tolerance-unexpected-js
import { GraphNode, StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const EmailAgentState = new StateSchema({
  draftResponse: z.string(),
});

const emailService = {
  send: async (body: string) => {
    throw new Error(`SMTP unavailable while sending: ${body}`);
  },
};

const sendReply: GraphNode<typeof EmailAgentState> = async (state) => {
  // Do not catch unexpected failures here. Let them bubble up and fail the run.
  await emailService.send(state.draftResponse);
  return state;
};
// :snippet-end:

// :remove-start:
import { END, START, StateGraph } from "@langchain/langgraph";

const graph = new StateGraph(EmailAgentState)
  .addNode("sendReply", sendReply)
  .addEdge(START, "sendReply")
  .addEdge("sendReply", END)
  .compile();

let bubbled = false;
try {
  await graph.invoke({ draftResponse: "Thanks for your email." });
} catch (error) {
  bubbled = error instanceof Error && error.message.includes("SMTP unavailable");
  if (!bubbled) throw error;
}
if (!bubbled) {
  throw new Error("expected Error to bubble up");
}
console.log("✓ langgraph-fault-tolerance-unexpected-js validated");
// :remove-end:
