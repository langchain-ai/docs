// :remove-start:
function sendEmail(_to: string): string {
  return "sent";
}
function validateEmail(_address: string): boolean {
  return true;
}
function webSearch(_query: string): string {
  return "web";
}
function databaseQuery(_sql: string): string {
  return "db";
}
function fileUpload(_path: string): string {
  return "uploaded";
}
// :remove-end:

// :snippet-start: subagents-email-tools-good-js
// ✅ Good: Focused tool set
const emailAgent = {
  name: "email-sender",
  tools: [sendEmail, validateEmail], // Only email-related
};
// :snippet-end:

// :snippet-start: subagents-email-tools-bad-js
// ❌ Bad: Too many tools
const emailAgentBad = {
  name: "email-sender",
  tools: [sendEmail, webSearch, databaseQuery, fileUpload], // Unfocused
};
// :snippet-end:

// :remove-start:
import { createDeepAgent } from "deepagents";

const focusedAgent = createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  subagents: [
    {
      description: "Sends and validates email",
      systemPrompt: "You send email messages.",
      ...emailAgent,
    },
  ],
});
const unfocusedAgent = createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  subagents: [
    {
      description: "Sends email but has too many tools",
      systemPrompt: "You send email messages.",
      ...emailAgentBad,
    },
  ],
});
if (!focusedAgent || !unfocusedAgent) throw new Error("agent not created");
console.log("✓ subagents-email-tools validated");
// :remove-end:
