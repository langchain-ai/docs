// Agents docs: steering middleware example.

// :snippet-start: agents-steering-js
import { createAgent, humanInTheLoopMiddleware, tool } from "langchain";
import * as z from "zod";

const search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [search],
  middleware: [humanInTheLoopMiddleware({ interruptOn: { writeFile: true } })],
});
// :snippet-end:

// :remove-start:
async function main() {
  void agent;
  console.log("✓ agents steering sample compiles");
}

main();
// :remove-end:

