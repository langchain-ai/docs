// :remove-start:
// CI holds the gateway key as LS_GATEWAY_KEY; the docs read LANGSMITH_API_KEY.
process.env.LANGSMITH_API_KEY = process.env.LS_GATEWAY_KEY || process.env.LANGSMITH_API_KEY;
// :remove-end:

// :snippet-start: llm-gateway-quickstart-chat-js
// :codegroup-tab: TypeScript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://gateway.smith.langchain.com/v1",
  apiKey: process.env.LANGSMITH_API_KEY,
});
const response = await client.chat.completions.create({
  // KEEP MODEL
  model: "anthropic/claude-opus-5",
  messages: [{ role: "user", content: "Explain what an LLM gateway does in one sentence." }],
});
console.log(response.choices[0].message.content);
// :snippet-end:
