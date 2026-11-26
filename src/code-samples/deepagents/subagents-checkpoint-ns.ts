// :snippet-start: subagents-checkpoint-ns-js
import { ToolMessage } from "langchain";
import { MemorySaver } from "@langchain/langgraph";
import { createDeepAgent } from "deepagents";

const checkpointer = new MemorySaver();
const agent = await createDeepAgent({
  model: "openai:gpt-6.1-sol",
  checkpointer,
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

// :remove-start:
if (!agent) throw new Error("agent not created");
if (!agent.getStateHistory) {
  throw new Error("agent is missing getStateHistory");
}
const openaiKey = process.env.OPENAI_API_KEY ?? "";
if (!openaiKey.startsWith("sk-")) {
  console.log(
    "✓ subagents-checkpoint-ns validated (skipped live invoke; OPENAI_API_KEY required)",
  );
  process.exit(0);
}
// :remove-end:
const threadId = "example-thread";
const result = await agent.invoke(
  {
    messages: [
      {
        role: "user",
        content: "Research one recent advance in quantum computing.",
      },
    ],
  },
  { configurable: { thread_id: threadId } },
);

const taskMessage = result.messages.find(
  (msg) => ToolMessage.isInstance(msg) && msg.name === "task",
);
const checkpointNs = taskMessage?.artifact?.checkpoint_ns;

if (checkpointNs) {
  for await (const snapshot of agent.getStateHistory({
    configurable: { thread_id: threadId, checkpoint_ns: checkpointNs },
  })) {
    console.log(snapshot.values);
  }
}
// :snippet-end:

// :remove-start:
if (!taskMessage) {
  throw new Error("expected a task ToolMessage from the coordinator");
}
if (!checkpointNs || typeof checkpointNs !== "string") {
  throw new Error(
    `expected artifact.checkpoint_ns on the task result, got ${String(checkpointNs)}`,
  );
}

let historyCount = 0;
for await (const snapshot of agent.getStateHistory({
  configurable: { thread_id: threadId, checkpoint_ns: checkpointNs },
})) {
  if (!snapshot.values) {
    throw new Error("expected snapshot.values in subagent history");
  }
  historyCount += 1;
}
if (historyCount === 0) {
  throw new Error("expected at least one checkpoint in subagent history");
}
console.log("✓ subagents-checkpoint-ns validated");
// :remove-end:
