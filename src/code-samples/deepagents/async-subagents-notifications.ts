// :remove-start:
import {
  addNotificationMetadata,
  AIMessage,
  HumanMessage,
} from "@langchain/core/messages";

const taskEvent = {
  task_id: "thread-123",
  agent_name: "researcher",
  status: "success",
  run_id: "run-456",
};
const state = {
  messages: [
    new HumanMessage("Research topic X"),
    new AIMessage("I have started the research."),
    addNotificationMetadata(
      new HumanMessage({
        content: [{ type: "text", text: "<task-notification>" }],
      }),
      { source: "async_subagent", data: taskEvent },
    ),
  ],
};
const seen: string[] = [];
// :remove-end:

// :snippet-start: async-subagents-notifications-js
import { getNotificationMetadata } from "@langchain/core/messages";

for (const message of state.messages) {
  const metadata = getNotificationMetadata(message);
  if (metadata?.source === "async_subagent") {
    const event = metadata.data as { agent_name: string; status: string };
    console.log(event.agent_name, event.status); // success, error, timeout, cancelled, or waiting
    // :remove-start:
    seen.push(event.status);
    // :remove-end:
  }
}
// :snippet-end:

// :remove-start:
if (seen.join() !== "success") {
  throw new Error(`unexpected notifications: ${seen}`);
}
console.log("✓ async-subagents-notifications sample validated");
// :remove-end:
