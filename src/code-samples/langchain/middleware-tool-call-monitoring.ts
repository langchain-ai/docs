// :snippet-start: middleware-tool-call-monitoring-js
import { createMiddleware } from "langchain";

const toolMonitoringMiddleware = createMiddleware({
  name: "ToolMonitoringMiddleware",
  wrapToolCall: (request, handler) => {
    console.log(`Executing tool: ${request.toolCall.name}`);
    console.log(`Arguments: ${JSON.stringify(request.toolCall.args)}`);
    try {
      const result = handler(request);
      console.log("Tool completed successfully");
      return result;
    } catch (e) {
      console.log(`Tool failed: ${e}`);
      throw e;
    }
  },
});
// :snippet-end:

// :remove-start:
async function main() {
  if (!toolMonitoringMiddleware) {
    throw new Error("toolMonitoringMiddleware should be defined");
  }
  console.log("✓ Tool call monitoring middleware definition is valid");
}
main();
// :remove-end:
