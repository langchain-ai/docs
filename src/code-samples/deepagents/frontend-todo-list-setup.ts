// :snippet-start: frontend-todo-list-setup-js
import { createDeepAgent } from "deepagents";
import { todoListMiddleware } from "langchain";

const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  middleware: [todoListMiddleware()],
});
// :snippet-end:

// :remove-start:
if (!agent) {
  throw new Error("agent not created");
}
console.log("✓ frontend-todo-list-setup sample validated");
// :remove-end:
