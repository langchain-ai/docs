// Managed Deep Agents quickstart, Tavily variant: the agent definition.
// Defining the agent needs no LangSmith call; deployment is `mda deploy`.

// :snippet-start: mda-quickstart-tavily-agent-js
// :codegroup-tab: agent.ts
import { defineDeepAgent } from "managed-deepagents";

import { internetSearch } from "./tools/search";

export const agent = defineDeepAgent({
  name: "research-assistant",
  // KEEP MODEL
  model: "openai:gpt-5.5",
  tools: [internetSearch],
});
// :snippet-end:

// :remove-start:
if (!agent) {
  throw new Error("agent was not defined");
}
console.log("✓ research-assistant defined with the Tavily search tool");
// :remove-end:
