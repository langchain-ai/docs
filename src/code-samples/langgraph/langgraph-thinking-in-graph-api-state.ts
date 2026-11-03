// :snippet-start: langgraph-thinking-in-graph-api-state-js
import { StateSchema } from "@langchain/langgraph";
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
// :snippet-end:

// :remove-start:
const classification: EmailClassification = {
  intent: "billing",
  urgency: "high",
  topic: "billing",
  summary: "Customer reports a billing problem",
};
EmailClassificationSchema.parse(classification);
if (!EmailAgentState) throw new Error("state schema not created");
console.log("✓ langgraph-thinking-in-graph-api-state-js validated");
// :remove-end:
