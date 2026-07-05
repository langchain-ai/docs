// :snippet-start: dynamic-subagents-fanout-configure-js
import { createDeepAgent } from "deepagents";
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  subagents: [{
    name: "reviewer",
    description: "Reviews code for security issues, citing lines and severity",
    systemPrompt: "You are a security-focused code reviewer. Read the file carefully and report any authentication or authorization issues with line numbers and severity.",
  }],
  middleware: [createCodeInterpreterMiddleware({ ptc: ["glob"] })],
});
// :snippet-end:

// :remove-start:
if (!agent) {
  throw new Error("agent not created");
}
console.log("✓ dynamic-subagents-fanout-configure");
// :remove-end:
