// :snippet-start: deepagents-sandbox-lifecycle-factory-thread-js
import { createDeepAgent, LangSmithSandbox } from "deepagents";
import { SandboxClient } from "langsmith/sandbox";
import type { LangGraphRunnableConfig } from "@langchain/langgraph";

const client = new SandboxClient();

export async function agent(config: LangGraphRunnableConfig) {
  const threadId = config.configurable?.thread_id as string; // [!code highlight]
  const sandboxName = `thread-${threadId}`;
  const existing = (await client.listSandboxes()).filter(
    (sb) => sb.name === sandboxName,
  );
  const lsSandbox =
    existing[0] ??
    (await client.createSandbox({
      name: sandboxName,
      idleTtlSeconds: 3600, // TTL: clean up when idle
    }));
  return createDeepAgent({
    model: "google_genai:gemini-3.5-flash",
    backend: new LangSmithSandbox({ sandbox: lsSandbox }),
  });
}
// :snippet-end:

// :remove-start:
if (typeof agent !== "function") {
  throw new Error("expected agent export");
}
console.log("✓ deepagents-sandbox-lifecycle-factory-thread-js validated");
// :remove-end:
