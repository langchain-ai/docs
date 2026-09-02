// :snippet-start: models-configure-params-provider-package-js
// :codegroup-tab: Provider package
import { ChatGoogle } from "@langchain/google";
import { createDeepAgent } from "deepagents";

const model = new ChatGoogle({
  // KEEP MODEL
  model: "gemini-3.1-pro-preview",
  reasoningEffort: "medium", // [!code highlight]
});
const agent = createDeepAgent({ model });
// :snippet-end:
