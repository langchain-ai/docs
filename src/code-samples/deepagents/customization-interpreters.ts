// :snippet-start: customization-interpreters-js
import { createDeepAgent } from "deepagents";
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";

const agent = createDeepAgent({
  model: "openai:gpt-6.1-sol",
  middleware: [createCodeInterpreterMiddleware()],
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
// :remove-end:
