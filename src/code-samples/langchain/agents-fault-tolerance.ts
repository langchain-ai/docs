// Agents docs: fault tolerance middleware example.

// :snippet-start: agents-fault-tolerance-js
import {
  createAgent,
  modelRetryMiddleware,
  tool,
  toolRetryMiddleware,
} from "langchain";
import * as z from "zod";

const search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [search],
  middleware: [
    modelRetryMiddleware({ maxRetries: 3 }),
    toolRetryMiddleware({ maxRetries: 2 }),
  ],
});
// :snippet-end:

// :remove-start:
async function main() {
  void agent;
  console.log("✓ agents fault tolerance sample compiles");
}

main();
// :remove-end:
