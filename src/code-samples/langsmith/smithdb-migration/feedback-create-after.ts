// :snippet-start: feedback-create-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
let runId = "<run-id>";
let sessionId = "<session-id>";
// :remove-start:
const project = await client.readProject({ projectName: "default" });
sessionId = project.id;
const found = await client.runs.query({
  project_ids: [sessionId],
  min_start_time: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  page_size: 1,
});
const runs = found.items ?? [];
if (runs.length === 0) {
  throw new Error("expected at least one run in the 'default' project");
}
runId = runs[0].id!;
// :remove-end:
await client.createFeedback(runId, "user_feedback", {
  score: 1,
  sessionId,
});
// :snippet-end:

// :remove-start:
console.log("✓ feedback-create-after validated");
// :remove-end:
