// :remove-start:
// streamEvents + nested subagents leave LangChainTracer unsettled
// ("No chain run to end"), which hangs async iterators under
// CODE_SAMPLE_TRACING=1. Disable tracing for this runnable harness only.
process.env.LANGSMITH_TRACING = "false";
process.env.LANGCHAIN_TRACING_V2 = "false";
// :remove-end:

// :snippet-start: subagent-stream-progress-js
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  name: "main-agent",
  systemPrompt:
    "You are a project coordinator with no research knowledge. " +
    "For every user request, you must call the task() tool with " +
    "subagent_type set to research-agent. Never answer research " +
    "questions yourself.",
  subagents: [
    {
      name: "research-agent",
      description:
        "Delegate research to this subagent. Give one topic at a time.",
      systemPrompt: "You are a great researcher. Return a brief summary.",
    },
  ],
});

async function streamSubagentProgress() {
  const stream = await agent.streamEvents(
    {
      messages: [
        {
          role: "user",
          content: "Research one recent advance in quantum computing.",
        },
      ],
    },
    { version: "v3" },
  );

  const coordinatorMessages: string[] = [];
  const subagentHandles: { name: string }[] = [];

  await Promise.all([
    (async () => {
      for await (const message of stream.messages) {
        const text = await message.text;
        console.log("[coordinator]", text);
        coordinatorMessages.push(text);
      }
    })(),
    (async () => {
      for await (const subagent of stream.subagents) {
        console.log(`[${subagent.name}] started`);
        subagentHandles.push({ name: subagent.name });
        for await (const message of subagent.messages) {
          console.log(`[${subagent.name}]`, await message.text);
        }
      }
    })(),
    stream.output,
  ]);

  return { coordinatorMessages, subagentHandles };
}
// :snippet-end:

// :remove-start:
async function main() {
  const { coordinatorMessages, subagentHandles } =
    await streamSubagentProgress();

  if (coordinatorMessages.length === 0) {
    throw new Error("expected coordinator messages");
  }
  if (subagentHandles.length === 0) {
    throw new Error(
      "expected at least one subagent handle; ensure the coordinator delegates via task()",
    );
  }
  if (subagentHandles[0].name !== "research-agent") {
    throw new Error(`expected research-agent, got ${subagentHandles[0].name}`);
  }
  console.log("✓ subagent stream progress sample completed");
}

await main();
// :remove-end:
