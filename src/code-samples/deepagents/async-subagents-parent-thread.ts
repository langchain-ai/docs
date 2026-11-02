// :snippet-start: async-subagents-parent-thread-js
import { Client } from "@langchain/langgraph-sdk";
import type { LangGraphRunnableConfig } from "@langchain/langgraph";
import { createDeepAgent } from "deepagents";

async function findSubagentThreads(parentThreadId: string) {
  const client = new Client();
  return client.threads.search({ metadata: { parent_thread_id: parentThreadId } });
}

function researcher(config: LangGraphRunnableConfig) {
  // Set when a supervisor launched this run with `start_async_task`
  const parentThreadId = config.metadata?.parent_thread_id;
  // :remove-start:
  if (parentThreadId !== "thread-supervisor") {
    throw new Error("expected the supervisor's thread");
  }
  // :remove-end:
  return createDeepAgent({
    model: "google:gemini-3.6-flash",
    systemPrompt: "You research topics thoroughly.",
  });
}
// :snippet-end:

// :remove-start:
if (typeof findSubagentThreads !== "function") {
  throw new Error("expected a function");
}
if (!researcher({ metadata: { parent_thread_id: "thread-supervisor" } })) {
  throw new Error("agent not created");
}
console.log("✓ async-subagents-parent-thread sample validated");
// :remove-end:
