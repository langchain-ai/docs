// :remove-start:
import { tool } from "langchain";
import * as z from "zod";

const webSearch = tool(async ({ query }) => `Results for: ${query}`, {
  name: "web_search",
  description: "Search the web",
  schema: z.object({ query: z.string() }),
});
// :remove-end:

// :snippet-start: context-engineering-research-subagent-js
const researchSubagent = {
  name: "researcher",
  description: "Conducts research on a topic",
  systemPrompt: `You are a research assistant.
    IMPORTANT: Return only the essential summary (under 500 words).
    Do NOT include raw search results or detailed tool outputs.`,
  tools: [webSearch],
};
// :snippet-end:

// :remove-start:
console.log("✓ context-engineering-research-subagent sample validated");
// :remove-end:
