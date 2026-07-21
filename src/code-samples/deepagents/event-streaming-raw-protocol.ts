// :remove-start:
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  systemPrompt:
    "You are a project coordinator with no creative writing knowledge. " +
    "For every user request, you must call the task() tool with " +
    "subagent_type set to writer-agent. Never answer creative requests yourself.",
  subagents: [
    {
      name: "writer-agent",
      description: "Delegate creative writing to this subagent.",
      systemPrompt: "You are a concise creative writer.",
    },
  ],
});

const input = {
  messages: [{ role: "user", content: "Write me a haiku about the sea" }],
};
// :remove-end:

// :snippet-start: event-streaming-raw-protocol-js
const stream = await agent.streamEvents(input, { version: "v3" });

const textDeltas: string[] = [];
for await (const event of stream) {
  if (event.method !== "messages") continue;

  const data = event.params.data;
  if (data.event !== "content-block-delta") continue;

  const block = data.delta ?? {};
  if (block.type === "text-delta") {
    const isSubagent = event.params.namespace.some((seg) =>
      seg.startsWith("tools:"),
    );
    const source = isSubagent ? "subagent" : "coordinator";
    console.log(`[${source}] ${block.text}`);
    textDeltas.push(block.text);
  }
}
// :snippet-end:

// :remove-start:
if (textDeltas.length === 0) {
  throw new Error("expected at least one text delta event");
}
console.log("✓ event-streaming-raw-protocol sample validated");
// :remove-end:
