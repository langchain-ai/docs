// :remove-start:
import { tool } from "langchain";
import * as z from "zod";

const webSearch = tool(async ({ query }) => `Results for: ${query}`, {
  name: "web_search",
  description: "Search the web",
  schema: z.object({ query: z.string() }),
});
// :remove-end:

// :snippet-start: context-engineering-research-subagent-js
const researchSubagent = {
  name: "researcher",
  description: "Conducts research on a topic",
  systemPrompt: `You are a research assistant.
    IMPORTANT: Return only the essential summary (under 500 words).
    Do NOT include raw search results or detailed tool outputs.`,
  tools: [webSearch],
};
// :snippet-end:

// :remove-start:
import { createDeepAgent } from "deepagents";
import { isAIMessage } from "@langchain/core/messages";

const agent = await createDeepAgent({
  model: "openai:gpt-5.5",
  systemPrompt:
    "You are a coordinator. For every request, call task() with subagent_type set to researcher.",
  subagents: [researchSubagent],
});

const result = await agent.invoke({
  messages: [
    {
      role: "user",
      content: "Research recent advances in quantum computing.",
    },
  ],
});

const delegated = (result.messages ?? []).some((message) => {
  if (!isAIMessage(message) || !message.tool_calls?.length) {
    return false;
  }
  return message.tool_calls.some((call) => call.name === "task");
});
if (!delegated) {
  throw new Error("expected coordinator to delegate via task()");
}

console.log("✓ context-engineering-research-subagent sample validated");
// :remove-end:
