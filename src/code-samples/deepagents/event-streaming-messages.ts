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

// :snippet-start: event-streaming-messages-js
const stream = await agent.streamEvents(input, { version: "v3" });

const coordinatorMessages: string[] = [];
for await (const message of stream.messages) {
  console.log("[coordinator]", await message.text);
  coordinatorMessages.push(await message.text);
}

for await (const subagent of stream.subagents) {
  for await (const message of subagent.messages) {
    console.log(`[${subagent.name}]`, await message.text);
  }
}
// :snippet-end:

// :remove-start:
if (coordinatorMessages.length === 0) {
  throw new Error("expected coordinator messages");
}
console.log("✓ event-streaming-messages sample validated");
// :remove-end:
