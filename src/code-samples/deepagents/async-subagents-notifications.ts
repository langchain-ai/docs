// :remove-start:
import { AIMessage, HumanMessage } from "@langchain/core/messages";

const event = {
  task_id: "thread-123",
  agent_name: "researcher",
  status: "success",
  run_id: "run-456",
};
const state = {
  messages: [
    new HumanMessage("Research topic X"),
    new AIMessage("Started task thread-123"),
    new HumanMessage({
      content: [{ type: "text", text: "[SYSTEM NOTIFICATION]" }],
      additional_kwargs: { deepagents_notification: event },
    }),
  ],
};
const seen: string[] = [];
// :remove-end:

// :snippet-start: async-subagents-notifications-js
for (const message of state.messages) {
  const event = message.additional_kwargs.deepagents_notification as
    | { agent_name: string; status: string }
    | undefined;
  if (event) {
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
