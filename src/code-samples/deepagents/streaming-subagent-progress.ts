// :snippet-start: streaming-subagent-progress-js
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

for await (const [namespace, chunk] of await agent.stream(
  {
    messages: [
      { role: "user", content: "Write a short summary about AI safety" },
    ],
  },
  { streamMode: "updates", subgraphs: true },
)) {
  // Main agent updates (empty namespace)
  if (namespace.length === 0) {
    for (const [nodeName, data] of Object.entries(chunk)) {
      if (nodeName === "tools") {
        // Subagent results returned to main agent
        for (const msg of (data as any).messages ?? []) {
          if (msg.type === "tool") {
            console.log(`\nSubagent complete: ${msg.name}`);
            console.log(`  Result: ${String(msg.content).slice(0, 200)}...`);
          }
        }
      } else {
        console.log(`[main agent] step: ${nodeName}`);
      }
    }
  }
  // Subagent updates (non-empty namespace)
  else {
    for (const [nodeName] of Object.entries(chunk)) {
      console.log(`  [${namespace[0]}] step: ${nodeName}`);
    }
  }
}
// :snippet-end:

// :remove-start:
console.log("✓ streaming-subagent-progress validated");
// :remove-end:
