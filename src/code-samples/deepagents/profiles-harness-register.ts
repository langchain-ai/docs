// :snippet-start: profiles-harness-register-js
import { registerHarnessProfile } from "deepagents";

registerHarnessProfile("openai:gpt-5.5", {
  systemPromptSuffix: "Respond in under 100 words.",
  excludedTools: ["execute"],
  excludedMiddleware: ["SummarizationMiddleware"],
  generalPurposeSubagent: { enabled: false },
});
// :snippet-end:

// :remove-start:
console.log("✓ profiles-harness-register sample validated");
// :remove-end:
