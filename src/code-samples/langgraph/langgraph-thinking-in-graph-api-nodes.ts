// :remove-start:
import { MemorySaver, START, StateGraph, StateSchema } from "@langchain/langgraph";
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
// :remove-end:

// :snippet-start: langgraph-thinking-in-graph-api-nodes-js
import {
  Command,
  END,
  type GraphNode,
  interrupt,
} from "@langchain/langgraph";

const readEmail: GraphNode<typeof EmailAgentState> = async (state) => {
  return {};
};

const classifyIntent: GraphNode<typeof EmailAgentState> = async (state) => {
  // Placeholder: replace with a real LLM call.
  // This heuristic matches the try-out sample so interrupt() runs.
  const lowered = state.emailContent.toLowerCase();
  let classification: EmailClassification;
  if (lowered.includes("charged") || lowered.includes("billing")) {
    classification = {
      intent: "billing",
      urgency: "high",
      topic: "billing",
      summary: "Customer reports a billing problem",
    };
  } else if (lowered.includes("crash") || lowered.includes("bug")) {
    classification = {
      intent: "bug",
      urgency: "medium",
      topic: "product bug",
      summary: "Customer reports a bug",
    };
  } else {
    classification = {
      intent: "question",
      urgency: "low",
      topic: "general",
      summary: "Customer question",
    };
  }

  let goto: "searchDocumentation" | "bugTracking" | "draftReply";
  if (classification.intent === "question" || classification.intent === "feature") {
    goto = "searchDocumentation";
  } else if (classification.intent === "bug") {
    goto = "bugTracking";
  } else {
    goto = "draftReply";
  }

  return new Command({ update: { classification }, goto });
};

const searchDocumentation: GraphNode<typeof EmailAgentState> = async (state) => {
  const classification = state.classification!;
  return new Command({
    update: { searchResults: [`Docs related to ${classification.topic}`] },
    goto: "draftReply",
  });
};

const bugTracking: GraphNode<typeof EmailAgentState> = async (state) => {
  const ticketId = "BUG-12345";
  return new Command({
    update: { searchResults: [`Bug ticket ${ticketId} created`] },
    goto: "draftReply",
  });
};

const draftResponse: GraphNode<typeof EmailAgentState> = async (state) => {
  const classification = state.classification!;
  const context = state.searchResults ?? [];
  let draft = `Thanks for your email about ${classification.topic}.`;
  if (context.length > 0) {
    draft += ` Context: ${context[0]}`;
  }

  const needsReview =
    classification.intent === "billing" ||
    classification.intent === "complex" ||
    classification.urgency === "high" ||
    classification.urgency === "critical";

  return new Command({
    update: { draftResponse: draft },
    goto: needsReview ? "humanReview" : "sendReply",
  });
};

const humanReview: GraphNode<typeof EmailAgentState> = async (state) => {
  const classification = state.classification!;

  // Nodes re-run from the start on resume. Keep work before interrupt() idempotent.
  const humanDecision = interrupt({
    emailId: state.emailId,
    originalEmail: state.emailContent,
    draftResponse: state.draftResponse,
    urgency: classification.urgency,
    intent: classification.intent,
    action: "Please review and approve/edit this response",
  });

  if (humanDecision?.approved) {
    return new Command({
      update: {
        draftResponse: humanDecision.editedResponse ?? state.draftResponse,
      },
      goto: "sendReply",
    });
  }
  // Rejection: human handles the email outside the graph
  return new Command({ update: {}, goto: END });
};

const sendReply: GraphNode<typeof EmailAgentState> = async (state) => {
  return {};
};
// :snippet-end:

// :remove-start:
async function main() {
  const app = new StateGraph(EmailAgentState)
    .addNode("readEmail", readEmail)
    .addNode("classifyIntent", classifyIntent, {
      ends: ["searchDocumentation", "bugTracking", "draftReply"],
    })
    .addNode("searchDocumentation", searchDocumentation, {
      ends: ["draftReply"],
    })
    .addNode("bugTracking", bugTracking, { ends: ["draftReply"] })
    .addNode("draftReply", draftResponse, {
      ends: ["humanReview", "sendReply"],
    })
    .addNode("humanReview", humanReview, { ends: ["sendReply", END] })
    .addNode("sendReply", sendReply)
    .addEdge(START, "readEmail")
    .addEdge("readEmail", "classifyIntent")
    .addEdge("sendReply", END)
    .compile({ checkpointer: new MemorySaver() });

  const input = {
    emailContent: "I was charged twice for my subscription! This is urgent!",
    senderEmail: "customer@example.com",
    emailId: "email_123",
  };

  // Approval path: pauses at humanReview, then resumes with an edited response.
  const config = { configurable: { thread_id: "nodes-approve" } };
  const paused = await app.invoke(input, config);
  const interrupts = (paused as { __interrupt__?: { value: any }[] }).__interrupt__;
  if (!interrupts || interrupts[0].value.intent !== "billing") {
    throw new Error(`Expected billing interrupt, got ${JSON.stringify(paused)}`);
  }
  await app.invoke(
    new Command({ resume: { approved: true, editedResponse: "Edited reply" } }),
    config
  );
  const approved = await app.getState(config);
  if (approved.next.length !== 0 || approved.values.draftResponse !== "Edited reply") {
    throw new Error(`Unexpected approved state: ${JSON.stringify(approved.values)}`);
  }

  // Rejection path: ends without sending.
  const rejectConfig = { configurable: { thread_id: "nodes-reject" } };
  await app.invoke(input, rejectConfig);
  await app.invoke(new Command({ resume: { approved: false } }), rejectConfig);
  const rejected = await app.getState(rejectConfig);
  if (rejected.next.length !== 0) {
    throw new Error("Expected rejected run to finish");
  }

  // Low-urgency question skips review and finishes without interrupting.
  const questionConfig = { configurable: { thread_id: "nodes-question" } };
  const question = await app.invoke(
    {
      emailContent: "How do I reset my password?",
      senderEmail: "customer@example.com",
      emailId: "email_789",
    },
    questionConfig
  );
  if ((question as { __interrupt__?: unknown }).__interrupt__) {
    throw new Error("Question should not interrupt");
  }
  if (!question.draftResponse?.includes("Docs related to general")) {
    throw new Error(`Unexpected question draft: ${question.draftResponse}`);
  }
  console.log("✓ langgraph-thinking-in-graph-api-nodes-js validated");
}

main();
// :remove-end:
