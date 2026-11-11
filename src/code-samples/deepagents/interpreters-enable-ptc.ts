// :snippet-start: interpreters-enable-ptc-js
import { createDeepAgent } from "deepagents";
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";

const agent = createDeepAgent({
  model: "openai:gpt-6.1-sol",
  middleware: [createCodeInterpreterMiddleware({ ptc: ["web_search"] })],
});
// :snippet-end:

// :remove-start:
if (!agent) {
  throw new Error("agent not created");
}
console.log("✓ interpreters-enable-ptc");
// :remove-end:
