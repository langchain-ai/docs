// :remove-start:
// CI holds the gateway key as LS_GATEWAY_KEY; the docs read LANGSMITH_API_KEY.
process.env.LANGSMITH_API_KEY = process.env.LS_GATEWAY_KEY || process.env.LANGSMITH_API_KEY;
// The docs tell the reader to export this in the shell.
process.env.LANGSMITH_GATEWAY = "true";
// :remove-end:

// :snippet-start: llm-gateway-quickstart-deepagents-js
// :codegroup-tab: TypeScript
// npm install deepagents
// export LANGSMITH_API_KEY="lsv2_..."
// export LANGSMITH_GATEWAY="true"
import { createDeepAgent } from "deepagents";

// KEEP MODEL
const agent = createDeepAgent({ model: "anthropic:claude-opus-5" });
const result = await agent.invoke({
  messages: [{ role: "user", content: "Explain what an LLM gateway does in one sentence." }],
});
console.log(result.messages[result.messages.length - 1].content);
// :snippet-end:
