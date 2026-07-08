// :remove-start:
function webSearch(_query: string): string {
  return "web";
}
function apiCall(_endpoint: string): string {
  return "api";
}
function databaseQuery(_sql: string): string {
  return "db";
}
function statisticalAnalysis(_data: string): string {
  return "stats";
}
function formatDocument(_content: string): string {
  return "formatted";
}
// :remove-end:

// :snippet-start: subagents-multiple-specialized-js
import { createDeepAgent } from "deepagents";

const subagents = [
  {
    name: "data-collector",
    description: "Gathers raw data from various sources",
    systemPrompt: "Collect comprehensive data on the topic",
    tools: [webSearch, apiCall, databaseQuery],
  },
  {
    name: "data-analyzer",
    description: "Analyzes collected data for insights",
    systemPrompt: "Analyze data and extract key insights",
    tools: [statisticalAnalysis],
  },
  {
    name: "report-writer",
    description: "Writes polished reports from analysis",
    systemPrompt: "Create professional reports from insights",
    tools: [formatDocument],
  },
];

const agent = createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  systemPrompt:
    "You coordinate data analysis and reporting. Use subagents for specialized tasks.",
  subagents: subagents,
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ subagents-multiple-specialized validated");
// :remove-end:
