// :remove-start:
async function search(query: string): Promise<string> {
  return query;
}

async function fetchUrl(url: string): Promise<string> {
  return url;
}
// :remove-end:

// :snippet-start: customization-overview-js
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  systemPrompt: "You are a helpful assistant.",
  tools: [search, fetchUrl],
  memory: ["./AGENTS.md"],
  skills: ["./skills/"],
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
// :remove-end:
