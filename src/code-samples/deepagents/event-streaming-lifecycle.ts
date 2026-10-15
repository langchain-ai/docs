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

// :snippet-start: event-streaming-lifecycle-js
const stream = await agent.streamEvents(input, { version: "v3" });

let running = 0;
let completed = 0;
let failed = 0;
const watchers: Promise<void>[] = [];

for await (const subagent of stream.subagents) {
  running += 1;
  console.log(`${subagent.name}: started`);

  watchers.push(
    subagent.output.then(
      () => {
        running -= 1;
        completed += 1;
        console.log(`${subagent.name}: completed`);
      },
      () => {
        running -= 1;
        failed += 1;
        console.log(`${subagent.name}: failed`);
      },
    ),
  );
}

await Promise.all(watchers);
console.log({ running, completed, failed });
// :snippet-end:

// :remove-start:
if (completed < 1) {
  throw new Error("expected at least one completed subagent");
}
console.log("✓ event-streaming-lifecycle sample validated");
// :remove-end:
