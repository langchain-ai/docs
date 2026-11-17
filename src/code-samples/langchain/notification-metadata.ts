// :snippet-start: notification-metadata-add-js
import { HumanMessage, addNotificationMetadata } from "@langchain/core/messages";

const notification = addNotificationMetadata(
  new HumanMessage("Background task t_42 finished."),
  { source: "background_job", data: { task_id: "t_42", status: "success" } },
);
// :snippet-end:

// :remove-start:
import { AIMessage } from "@langchain/core/messages";

const messages = [
  new HumanMessage("Summarize the report."),
  new AIMessage("Working on it."),
  notification,
];
const labels: string[] = [];
// :remove-end:

// :snippet-start: notification-metadata-read-js
import { getNotificationMetadata } from "@langchain/core/messages";

for (const message of messages) {
  const metadata = getNotificationMetadata(message);
  if (metadata === undefined) {
    console.log(message.text); // A regular message
  } else {
    console.log(`[${metadata.source}]`, metadata.data);
    // :remove-start:
    labels.push(metadata.source);
    // :remove-end:
  }
}
// :snippet-end:

// :remove-start:
if (notification.content !== "Background task t_42 finished.") {
  throw new Error("content changed");
}
if (labels.join() !== "background_job") {
  throw new Error(`unexpected labels: ${labels}`);
}
if (getNotificationMetadata(messages[0]) !== undefined) {
  throw new Error("regular message was tagged");
}
console.log("✓ notification-metadata sample validated");
// :remove-end:
