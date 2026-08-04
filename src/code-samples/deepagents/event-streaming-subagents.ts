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
// :remove-end:

// :snippet-start: event-streaming-subagents-js
const stream = await agent.streamEvents(
  { messages: [{ role: "user", content: "Write me a haiku about the sea" }] },
  { version: "v3" },
);

const subagentNames: string[] = [];
for await (const subagent of stream.subagents) {
  console.log(subagent.name);
  console.log(await subagent.taskInput);

  for await (const message of subagent.messages) {
    console.log(await message.text);
  }

  subagentNames.push(subagent.name);
}
// :snippet-end:

// :remove-start:
if (subagentNames.length === 0) {
  throw new Error("expected at least one subagent handle");
}
if (subagentNames[0] !== "writer-agent") {
  throw new Error(`expected writer-agent, got ${subagentNames[0]}`);
}
console.log("✓ event-streaming-subagents sample validated");
// :remove-end:
