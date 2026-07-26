// :snippet-start: models-configure-params-init-chat-model-js
// :codegroup-tab: initChatModel
import { initChatModel } from "langchain/chat_models/universal";
import { createDeepAgent } from "deepagents";

const model = await initChatModel("google-genai:gemini-3.5-flash", {
  reasoningEffort: "medium", // [!code highlight]
});
const agent = createDeepAgent({ model });
// :snippet-end:
