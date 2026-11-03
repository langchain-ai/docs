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

// :snippet-start: streaming-llm-tokens-js
let currentSource = "";

for await (const [namespace, chunk] of await agent.stream(
  {
    messages: [
      {
        role: "user",
        content: "Research quantum computing advances",
      },
    ],
  },
  { streamMode: "messages", subgraphs: true },
)) {
  const [message] = chunk;

  // Check if this event came from a subagent (namespace contains "tools:")
  const isSubagent = namespace.some((s: string) => s.startsWith("tools:"));

  if (isSubagent) {
    // Token from a subagent
    const subagentNs = namespace.find((s: string) => s.startsWith("tools:"))!;
    if (subagentNs !== currentSource) {
      process.stdout.write(`\n\n--- [subagent: ${subagentNs}] ---\n`);
      currentSource = subagentNs;
    }
    if (message.text) {
      process.stdout.write(message.text);
    }
  } else {
    // Token from the main agent
    if ("main" !== currentSource) {
      process.stdout.write(`\n\n--- [main agent] ---\n`);
      currentSource = "main";
    }
    if (message.text) {
      process.stdout.write(message.text);
    }
  }
}

process.stdout.write("\n");
// :snippet-end:

// :remove-start:
console.log("✓ streaming-llm-tokens validated");
// :remove-end:
