// :snippet-start: tool-error-handling-js
import { createAgent, createMiddleware, ToolMessage } from "langchain";

const handleToolErrors = createMiddleware({
  name: "HandleToolErrors",
  wrapToolCall: async (request, handler) => {
    try {
      return await handler(request);
    } catch (error) {
      return new ToolMessage({
        content: `Tool error: Please check your input and try again. (${error})`,
        tool_call_id: request.toolCall.id!,
      });
    }
  },
});

const agent = createAgent({
  model: "claude-sonnet-4-6",
  tools: [],
  middleware: [handleToolErrors],
});
// :snippet-end:

// :remove-start:
async function main() {
  const result = await handleToolErrors.wrapToolCall!(
    { toolCall: { id: "1" } } as any,
    async () => {
      throw new Error("division by zero");
    },
  );

  if (!(result instanceof ToolMessage)) {
    throw new Error("Expected a ToolMessage result");
  }
  if (result.tool_call_id !== "1") {
    throw new Error(`Expected tool_call_id "1", got "${result.tool_call_id}"`);
  }
  if (!result.content.includes("division by zero")) {
    throw new Error(`Expected error text in content, got "${result.content}"`);
  }

  console.log("✓ tool errors convert to ToolMessage");
}

main();
// :remove-end:
