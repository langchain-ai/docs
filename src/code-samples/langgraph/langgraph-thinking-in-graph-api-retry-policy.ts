// :remove-start:
import { StateGraph, StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const EmailAgentState = new StateSchema({
  emailContent: z.string(),
  draftResponse: z.string().optional(),
});

const searchDocumentation = async () => ({ draftResponse: "docs" });

const workflow = new StateGraph(EmailAgentState);
// :remove-end:

// :snippet-start: langgraph-thinking-in-graph-api-retry-policy-js
workflow.addNode("searchDocumentation", searchDocumentation, {
  retryPolicy: { maxAttempts: 3 },
});
// :snippet-end:

// :remove-start:
const compiled = workflow
  .addEdge("__start__", "searchDocumentation")
  .addEdge("searchDocumentation", "__end__")
  .compile();
const result = await compiled.invoke({ emailContent: "hello" });
if (result.draftResponse !== "docs") {
  throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
}
console.log("✓ langgraph-thinking-in-graph-api-retry-policy-js validated");
// :remove-end:
