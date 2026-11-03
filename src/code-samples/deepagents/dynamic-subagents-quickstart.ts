// :snippet-start: dynamic-subagents-quickstart-js
import { createDeepAgent } from "deepagents";
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  subagents: [{
    name: "reviewer",
    description: "Reviews code for security issues, citing lines and severity",
    systemPrompt: "You are a security-focused code reviewer. Report issues with line numbers and severity.",
  }],
  middleware: [createCodeInterpreterMiddleware()],
});
// :snippet-end:

// :snippet-start: dynamic-subagents-invoke-js
const result = await agent.invoke({
  messages: [{ role: "user", content: "Run a workflow that reviews every file in src/routes/ and summarizes the top risks." }],
});
// :snippet-end:

// :remove-start:
if (!agent) {
  throw new Error("agent not created");
}
if (!result) {
  throw new Error("expected invoke result");
}
console.log("✓ dynamic-subagents-quickstart");
// :remove-end:
