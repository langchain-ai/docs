// :snippet-start: subagents-troubleshooting-concise-prompt-js
const systemPrompt = `...

IMPORTANT: Return only the essential summary.
Do NOT include raw data, intermediate search results, or detailed tool outputs.
Your response should be under 500 words.`;
// :snippet-end:

// :snippet-start: subagents-troubleshooting-filesystem-prompt-js
const filesystemPrompt = `When you gather large amounts of data:
1. Save raw data to /data/raw_results.txt
2. Process and analyze the data
3. Return only the analysis summary

This keeps context clean.`;
// :snippet-end:

// :remove-start:
import { createDeepAgent } from "deepagents";

const conciseAgent = createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  subagents: [
    {
      name: "research-agent",
      description: "Researches topics and returns concise summaries",
      systemPrompt,
    },
  ],
});
const filesystemAgent = createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  subagents: [
    {
      name: "data-analyst",
      description: "Analyzes large datasets via the filesystem",
      systemPrompt: filesystemPrompt,
    },
  ],
});
if (!conciseAgent || !filesystemAgent) throw new Error("agent not created");
console.log("✓ subagents-troubleshooting-prompts validated");
// :remove-end:
