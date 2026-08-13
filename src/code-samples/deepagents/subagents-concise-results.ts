// :snippet-start: subagents-concise-results-js
const dataAnalyst = {
  systemPrompt: `Analyze the data and return:
  1. Key insights (3-5 bullet points)
  2. Overall confidence score
  3. Recommended next actions

  Do NOT include:
  - Raw data
  - Intermediate calculations
  - Detailed tool outputs

  Keep response under 300 words.`,
};
// :snippet-end:

// :remove-start:
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  subagents: [
    {
      name: "data-analyst",
      description: "Analyzes data and returns concise summaries",
      ...dataAnalyst,
    },
  ],
});
if (!agent) throw new Error("agent not created");
console.log("✓ subagents-concise-results validated");
// :remove-end:
