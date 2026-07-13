// :remove-start:
if (!process.env.ANTHROPIC_API_KEY) {
  console.log("[rag-deep-baseline] Skipping (ANTHROPIC_API_KEY required).");
  process.exit(0);
}
// :remove-end:

// :snippet-start: rag-deep-baseline-js
import "dotenv/config";

import { createDeepAgent } from "deepagents";
import { HumanMessage } from "langchain";

const EXAMPLE_QUERY =
  "How do I stream intermediate tool results from a subagent?";

const baselineAgent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [],
  systemPrompt:
    "You are a helpful LangChain documentation assistant. Answer questions about LangChain APIs and patterns.",
});

const result = await baselineAgent.invoke({
  messages: [new HumanMessage(EXAMPLE_QUERY)],
});

console.log(result.messages.at(-1)?.text);
// :snippet-end:

// :remove-start:
if (!result.messages.at(-1)?.text) {
  throw new Error("Expected baseline agent response");
}
console.log("✓ rag-deep-baseline");
// :remove-end:
