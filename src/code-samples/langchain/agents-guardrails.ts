// Agents docs: guardrails middleware example.

// :snippet-start: agents-guardrails-js
import { createAgent, piiMiddleware, tool } from "langchain";
import * as z from "zod";

const search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [search],
  middleware: [piiMiddleware("email")],
});
// :snippet-end:

// :remove-start:
async function main() {
  void agent;
  console.log("✓ agents guardrails sample compiles");
}

main();
// :remove-end:
