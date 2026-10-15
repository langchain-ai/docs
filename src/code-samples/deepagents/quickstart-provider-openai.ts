// :remove-start:
if (!process.env.OPENAI_API_KEY) {
  console.log(
    "[quickstart-provider-openai] Skipping (OPENAI_API_KEY required).",
  );
  process.exit(0);
}
// :remove-end:

// :snippet-start: quickstart-search-tool-provider-openai-js
// :codegroup-tab: OpenAI
import { createDeepAgent } from "deepagents";

// OpenAI's built-in web search — no extra install or API key needed
const internetSearch = { type: "web_search_preview" };
// :snippet-end:

// :remove-start:
const researchInstructions = `You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## \`internet_search\`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
`;

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  tools: [internetSearch],
  systemPrompt: researchInstructions,
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "What is langgraph?" }],
});

if (!result?.messages?.[result.messages.length - 1]?.content) {
  throw new Error("No result returned");
}
console.log("✓ quickstart-provider-openai");
// :remove-end:
