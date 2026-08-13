// :remove-start:
function internetSearch(_query: string): string {
  return "search results";
}
// :remove-end:

// :snippet-start: subagents-research-prompt-js
const researchSubagent = {
  name: "research-agent",
  description:
    "Conducts in-depth research using web search and synthesizes findings",
  systemPrompt: `You are a thorough researcher. Your job is to:

  1. Break down the research question into searchable queries
  2. Use internet_search to find relevant information
  3. Synthesize findings into a comprehensive but concise summary
  4. Cite sources when making claims

  Output format:
  - Summary (2-3 paragraphs)
  - Key findings (bullet points)
  - Sources (with URLs)

  Keep your response under 500 words to maintain clean context.`,
  tools: [internetSearch],
};
// :snippet-end:

// :remove-start:
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  subagents: [researchSubagent],
});
if (!agent) throw new Error("agent not created");
console.log("✓ subagents-research-prompt validated");
// :remove-end:
