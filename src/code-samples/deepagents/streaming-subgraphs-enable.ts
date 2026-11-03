// :snippet-start: streaming-subgraphs-enable-js
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  systemPrompt: "You are a helpful research assistant",
  subagents: [
    {
      name: "researcher",
      description: "Researches a topic in depth",
      systemPrompt: "You are a thorough researcher.",
    },
  ],
});

for await (const [namespace, chunk] of await agent.stream(
  {
    messages: [
      { role: "user", content: "Research quantum computing advances" },
    ],
  },
  {
    streamMode: "updates",
    subgraphs: true, // [!code highlight]
  },
)) {
  if (namespace.length > 0) {
    // Subagent event - namespace identifies the source
    console.log(`[subagent: ${namespace.join("|")}]`);
  } else {
    // Main agent event
    console.log("[main agent]");
  }
  console.log(chunk);
}
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("expected agent from subgraphs enable sample");
console.log("✓ streaming-subgraphs-enable validated");
// :remove-end:
