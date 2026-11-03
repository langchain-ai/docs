// :snippet-start: dynamic-subagents-loop-configure-js
import { createDeepAgent } from "deepagents";
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  subagents: [{
    name: "analyzer",
    description: "Analyzes code for unused exports, functions, and dead code paths",
    systemPrompt: "You are a code analyst specializing in dead code detection. Find unused exports, unreachable functions, and orphaned modules. Report each with file path and evidence.",
  }],
  middleware: [createCodeInterpreterMiddleware()],
});
// :snippet-end:

// :remove-start:
if (!agent) {
  throw new Error("agent not created");
}
console.log("✓ dynamic-subagents-loop-configure");
// :remove-end:
