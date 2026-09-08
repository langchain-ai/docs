// :snippet-start: feedback-create-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
let runId = "<run-id>";
// :remove-start:
const runs = [];
for await (const run of client.listRuns({ projectName: "default", limit: 1 })) {
  runs.push(run);
}
if (runs.length === 0) {
  throw new Error("expected at least one run in the 'default' project");
}
runId = runs[0].id;
// :remove-end:
await client.createFeedback(runId, "user_feedback", {
  score: 1,
});
// :snippet-end:

// :remove-start:
console.log("✓ feedback-create-before validated");
// :remove-end:
