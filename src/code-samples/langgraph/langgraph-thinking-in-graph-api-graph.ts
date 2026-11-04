// :remove-start:
// Harness copies of the state and nodes from the earlier snippets. Aliased
// imports avoid clashing with the imports that the snippets below show.
import {
  Command as NodeCommand,
  END as NODE_END,
  type GraphNode,
  interrupt,
  StateSchema,
} from "@langchain/langgraph";
import * as z from "zod";

const EmailClassificationSchema = z.object({
  intent: z.enum(["question", "bug", "billing", "feature", "complex"]),
  urgency: z.enum(["low", "medium", "high", "critical"]),
  topic: z.string(),
  summary: z.string(),
});

const EmailAgentState = new StateSchema({
  emailContent: z.string(),
  senderEmail: z.string(),
  emailId: z.string(),
  classification: EmailClassificationSchema.optional(),
  searchResults: z.array(z.string()).optional(),
  draftResponse: z.string().optional(),
});

type EmailClassification = z.infer<typeof EmailClassificationSchema>;

const readEmail: GraphNode<typeof EmailAgentState> = async () => ({});

const classifyIntent: GraphNode<typeof EmailAgentState> = async (state) => {
  const lowered = state.emailContent.toLowerCase();
  let classification: EmailClassification;
  if (lowered.includes("charged") || lowered.includes("billing")) {
    classification = {
      intent: "billing",
      urgency: "high",
      topic: "billing",
      summary: "Customer reports a billing problem",
    };
  } else {
    classification = {
      intent: "question",
      urgency: "low",
      topic: "general",
      summary: "Customer question",
    };
  }
  const goto = classification.intent === "question" ? "searchDocumentation" : "draftReply";
  return new NodeCommand({ update: { classification }, goto });
};

const searchDocumentation: GraphNode<typeof EmailAgentState> = async (state) => {
  return new NodeCommand({
    update: { searchResults: [`Docs related to ${state.classification!.topic}`] },
    goto: "draftReply",
  });
};

const bugTracking: GraphNode<typeof EmailAgentState> = async () => {
  return new NodeCommand({
    update: { searchResults: ["Bug ticket BUG-12345 created"] },
    goto: "draftReply",
  });
};

const draftResponse: GraphNode<typeof EmailAgentState> = async (state) => {
  const classification = state.classification!;
  const needsReview =
    classification.intent === "billing" || classification.urgency === "high";
  return new NodeCommand({
    update: { draftResponse: `Thanks for your email about ${classification.topic}.` },
    goto: needsReview ? "humanReview" : "sendReply",
  });
};

const humanReview: GraphNode<typeof EmailAgentState> = async (state) => {
  const humanDecision = interrupt({ draftResponse: state.draftResponse });
  if (humanDecision?.approved) {
    return new NodeCommand({
      update: { draftResponse: humanDecision.editedResponse ?? state.draftResponse },
      goto: "sendReply",
    });
  }
  return new NodeCommand({ update: {}, goto: NODE_END });
};

const sendReply: GraphNode<typeof EmailAgentState> = async () => ({});
// :remove-end:

// :snippet-start: langgraph-thinking-in-graph-api-graph-js
import { END, MemorySaver, START, StateGraph } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const app = new StateGraph(EmailAgentState)
  .addNode("readEmail", readEmail)
  .addNode("classifyIntent", classifyIntent, {
    ends: ["searchDocumentation", "bugTracking", "draftReply"],
  })
  .addNode("searchDocumentation", searchDocumentation, {
    ends: ["draftReply"],
    retryPolicy: { maxAttempts: 3 },
  })
  .addNode("bugTracking", bugTracking, {
    ends: ["draftReply"],
    retryPolicy: { maxAttempts: 3 },
  })
  .addNode("draftReply", draftResponse, {
    ends: ["humanReview", "sendReply"],
  })
  .addNode("humanReview", humanReview, {
    ends: ["sendReply", END],
  })
  .addNode("sendReply", sendReply)
  .addEdge(START, "readEmail")
  .addEdge("readEmail", "classifyIntent")
  .addEdge("sendReply", END)
  .compile({ checkpointer });
// :snippet-end:

// :remove-start:
const graphNodes = Object.keys((await app.getGraphAsync()).nodes);
for (const name of [
  "readEmail",
  "classifyIntent",
  "searchDocumentation",
  "bugTracking",
  "draftReply",
  "humanReview",
  "sendReply",
]) {
  if (!graphNodes.includes(name)) throw new Error(`Missing node: ${name}`);
}
console.log("✓ langgraph-thinking-in-graph-api-graph-js validated");
// :remove-end:

// :snippet-start: langgraph-thinking-in-graph-api-try-out-js
import { Command } from "@langchain/langgraph";

const config = { configurable: { thread_id: "customer_123" } };

const result = await app.invoke(
  {
    emailContent: "I was charged twice for my subscription! This is urgent!",
    senderEmail: "customer@example.com",
    emailId: "email_123",
  },
  config
);
// The graph pauses at humanReview when urgency is high

await app.invoke(
  new Command({
    resume: {
      approved: true,
      editedResponse:
        "We sincerely apologize for the double charge. I've initiated an immediate refund...",
    },
  }),
  config
);
// :snippet-end:

// :remove-start:
const interrupts = (result as { __interrupt__?: unknown[] }).__interrupt__;
if (!interrupts || interrupts.length !== 1) {
  throw new Error(`Expected one interrupt, got ${JSON.stringify(result)}`);
}
const finalState = await app.getState(config);
if (finalState.next.length !== 0) {
  throw new Error(`Expected run to finish, next=${finalState.next}`);
}
if (!finalState.values.draftResponse?.startsWith("We sincerely apologize")) {
  throw new Error(`Unexpected draft: ${finalState.values.draftResponse}`);
}
console.log("✓ langgraph-thinking-in-graph-api-try-out-js validated");
// :remove-end:
