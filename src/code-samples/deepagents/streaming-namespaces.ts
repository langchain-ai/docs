// :remove-start:
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
// :remove-end:

// :snippet-start: streaming-namespaces-js
for await (const [namespace, chunk] of await agent.stream(
  { messages: [{ role: "user", content: "Plan my vacation" }] },
  { streamMode: "updates", subgraphs: true },
)) {
  // Check if this event came from a subagent
  const isSubagent = namespace.some((segment: string) =>
    segment.startsWith("tools:"),
  );

  if (isSubagent) {
    // Extract the tool call ID from the namespace
    const toolCallId = namespace
      .find((s: string) => s.startsWith("tools:"))
      ?.split(":")[1];
    console.log(`Subagent ${toolCallId}:`, chunk);
  } else {
    console.log("Main agent:", chunk);
  }
}
// :snippet-end:

// :remove-start:
console.log("✓ streaming-namespaces validated");
// :remove-end:
