// :snippet-start: customization-system-prompt-js
import { createDeepAgent } from "deepagents";

const researchInstructions =
  `You are an expert researcher. ` +
  `Your job is to conduct thorough research, and then ` +
  `write a polished report.`;

const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  systemPrompt: researchInstructions,
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
// :remove-end:
