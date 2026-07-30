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

// :snippet-start: event-streaming-tool-calls-js
const stream = await agent.streamEvents(input, { version: "v3" });

const coordinatorToolNames: string[] = [];
for await (const call of stream.toolCalls) {
  console.log("[coordinator tool]", call.name, call.input);
  console.log(await call.status);
  coordinatorToolNames.push(call.name);
}

for await (const subagent of stream.subagents) {
  for await (const call of subagent.toolCalls) {
    console.log(`[${subagent.name} tool]`, call.name, call.input);

    const status = await call.status;
    if (status === "finished") {
      console.log(await call.output);
    } else if (status === "error") {
      console.error(await call.error);
    }
  }
}
// :snippet-end:

// :remove-start:
if (coordinatorToolNames.length === 0) {
  throw new Error("expected at least one coordinator tool call");
}
if (coordinatorToolNames[0] !== "task") {
  throw new Error(`expected task tool call, got ${coordinatorToolNames[0]}`);
}
console.log("✓ event-streaming-tool-calls sample validated");
// :remove-end:
