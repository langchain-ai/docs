// :remove-start:
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  systemPrompt:
    "You are a project coordinator with no research knowledge. " +
    "For every user request, you must call the task() tool with " +
    "subagent_type set to researcher. Never answer research questions yourself. " +
    "Keep your final response to one sentence.",
  subagents: [
    {
      name: "researcher",
      description: "Researches topics thoroughly",
      systemPrompt:
        "You are a thorough researcher. Research the given topic " +
        "and provide a concise summary in 2-3 sentences.",
    },
  ],
});
// :remove-end:

// :snippet-start: streaming-lifecycle-js
const activeSubagents = new Map<
  string,
  { type?: string; description?: string; status: string }
>();

for await (const [namespace, chunk] of await agent.stream(
  {
    messages: [
      { role: "user", content: "Research the latest AI safety developments" },
    ],
  },
  { streamMode: "updates", subgraphs: true },
)) {
  for (const [nodeName, data] of Object.entries(chunk)) {
    // ─── Phase 1: Detect subagent starting ────────────────────────
    // When the main agent's model_request contains task tool calls,
    // a subagent has been spawned.
    if (namespace.length === 0 && nodeName === "model_request") {
      for (const msg of (data as any).messages ?? []) {
        for (const tc of msg.tool_calls ?? []) {
          if (tc.name === "task") {
            activeSubagents.set(tc.id, {
              type: tc.args?.subagent_type,
              description: tc.args?.description?.slice(0, 80),
              status: "pending",
            });
            console.log(
              `[lifecycle] PENDING  → subagent "${tc.args?.subagent_type}" (${tc.id})`,
            );
          }
        }
      }
    }

    // ─── Phase 2: Detect subagent running ─────────────────────────
    // When we receive events from a tools:UUID namespace, that
    // subagent is actively executing.
    if (namespace.length > 0 && namespace[0].startsWith("tools:")) {
      const pregelId = namespace[0].split(":")[1];
      // Check if any pending subagent needs to be marked running.
      // Note: the pregel task ID differs from the tool_call_id,
      // so we mark any pending subagent as running on first subagent event.
      for (const [id, sub] of activeSubagents) {
        if (sub.status === "pending") {
          sub.status = "running";
          console.log(
            `[lifecycle] RUNNING  → subagent "${sub.type}" (pregel: ${pregelId})`,
          );
          break;
        }
      }
    }

    // ─── Phase 3: Detect subagent completing ──────────────────────
    // When the main agent's tools node returns a tool message,
    // the subagent has completed and returned its result.
    if (namespace.length === 0 && nodeName === "tools") {
      for (const msg of (data as any).messages ?? []) {
        if (msg.type === "tool") {
          const subagent = activeSubagents.get(msg.tool_call_id);
          if (subagent) {
            subagent.status = "complete";
            console.log(
              `[lifecycle] COMPLETE → subagent "${subagent.type}" (${msg.tool_call_id})`,
            );
            console.log(
              `  Result preview: ${String(msg.content).slice(0, 120)}...`,
            );
          }
        }
      }
    }
  }
}

// Print final state
console.log("\n--- Final subagent states ---");
for (const [id, sub] of activeSubagents) {
  console.log(`  ${sub.type}: ${sub.status}`);
}
// :snippet-end:

// :remove-start:
if (activeSubagents.size === 0) {
  throw new Error("expected at least one tracked subagent in lifecycle sample");
}
console.log("✓ streaming-lifecycle validated");
// :remove-end:
