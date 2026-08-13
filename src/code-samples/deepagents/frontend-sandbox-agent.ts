// :snippet-start: frontend-sandbox-agent-js
import { createDeepAgent } from "deepagents";
import type { LangGraphRunnableConfig } from "@langchain/langgraph";

import { getOrCreateSandboxForThread } from "./api/utils.js";

export async function agent(config: LangGraphRunnableConfig) {
  const threadId = config.configurable?.thread_id;
  if (!threadId) throw new Error("No thread_id — agent must run on a thread");

  const backend = await getOrCreateSandboxForThread(threadId);

  return createDeepAgent({
    model: "google_genai:gemini-3.5-flash",
    backend,
    systemPrompt: "You are an expert developer working on a project in /app.",
  });
}
// :snippet-end:

// :remove-start:
if (typeof agent !== "function") {
  throw new Error("expected agent export");
}
console.log("✓ frontend-sandbox-agent-js validated");
// :remove-end:
