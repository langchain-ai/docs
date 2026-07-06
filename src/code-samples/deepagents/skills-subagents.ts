// :remove-start:
function webSearch(_query: string): string {
  return "search results";
}
// :remove-end:

// :snippet-start: skills-subagents-js
import { createDeepAgent } from "deepagents";

const researchSubagent = {
  name: "researcher",
  description: "Research assistant with specialized skills",
  systemPrompt: "You are a researcher.",
  tools: [webSearch],
  skills: ["/skills/research/", "/skills/web-search/"], // Subagent-specific skills
};

// KEEP MODEL
const agent = await createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  skills: ["/skills/main/"], // Main agent and GP subagent get these
  subagents: [researchSubagent], // Researcher gets only its own skills
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ skills-subagents sample validated");
// :remove-end:
