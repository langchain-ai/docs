// :remove-start:
function readDocument(_path: string): string {
  return "doc";
}
function analyzeContract(_path: string): string {
  return "analysis";
}
function getStockPrice(_symbol: string): string {
  return "price";
}
function analyzeFundamentals(_symbol: string): string {
  return "fundamentals";
}
// :remove-end:

// :snippet-start: subagents-choose-models-js
const subagents = [
  {
    name: "contract-reviewer",
    description: "Reviews legal documents and contracts",
    systemPrompt: "You are an expert legal reviewer...",
    tools: [readDocument, analyzeContract],
    model: "google:gemini-4-hydrogen", // Large context for long documents
  },
  {
    name: "financial-analyst",
    description: "Analyzes financial data and market trends",
    systemPrompt: "You are an expert financial analyst...",
    tools: [getStockPrice, analyzeFundamentals],
    model: "openai:gpt-6.1-sol", // Better for numerical analysis
  },
];
// :snippet-end:

// :remove-start:
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "google:gemini-4-hydrogen",
  subagents,
});
if (!agent) throw new Error("agent not created");
console.log("✓ subagents-choose-models validated");
// :remove-end:
