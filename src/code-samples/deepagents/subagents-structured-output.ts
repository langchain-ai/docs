// :snippet-start: subagents-structured-output-js
import { z } from "zod";
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";

const webSearch = tool(
  async ({ query }: { query: string }) => `web results for ${query}`,
  {
    name: "web_search",
    description: "Search the web",
    schema: z.object({ query: z.string() }),
  },
);

const ResearchFindings = z.object({
  summary: z.string().describe("Summary of findings"),
  confidence: z.number().describe("Confidence score from 0 to 1"),
  sources: z.array(z.string()).describe("List of source URLs"),
});

const researchSubagent = {
  name: "researcher",
  description: "Researches topics and returns structured findings",
  systemPrompt: "Research the given topic thoroughly. Return your findings.",
  tools: [webSearch],
  responseFormat: ResearchFindings,
};

const agent = createDeepAgent({
  model: "claude-sonnet-4-6",
  subagents: [researchSubagent],
});

const result = await agent.invoke({
  messages: [
    { role: "user", content: "Research recent advances in quantum computing" },
  ],
});

// The parent's ToolMessage contains JSON-serialized structured data:
// '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ subagents-structured-output validated");
// :remove-end:
