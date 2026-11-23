// :remove-start:
process.env.OPENAI_API_KEY ??= "sk-test-key";
// :remove-end:

// :snippet-start: models-init-chat-openai-compatible-js
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-5.4-mini", {
  modelProvider: "openai",
  baseUrl: "https://api.openai.com/v1",
  apiKey: process.env.OPENAI_API_KEY,
});
// :snippet-end:

// :remove-start:
if (!model) throw new Error("expected model");
console.log("✓ models-init-chat-openai-compatible validated");
// :remove-end:
