// :snippet-start: async-subagents-answer-waiting-js
import { Client } from "@langchain/langgraph-sdk";

async function answerWaitingSubagent(
  taskId: string,
  graphId: string,
  answer: unknown,
): Promise<void> {
  const client = new Client(); // Pass apiUrl for a subagent on another deployment
  const thread = await client.threads.get(taskId); // The task ID is the subagent's thread ID
  const [interrupt] = Object.values(thread.interrupts ?? {})[0];
  await client.runs.create(taskId, graphId, {
    command: { resume: { [interrupt.id!]: answer } },
  });
}
// :snippet-end:

// :remove-start:
if (typeof answerWaitingSubagent !== "function") {
  throw new Error("expected a function");
}
console.log("✓ async-subagents-answer-waiting sample validated");
// :remove-end:
