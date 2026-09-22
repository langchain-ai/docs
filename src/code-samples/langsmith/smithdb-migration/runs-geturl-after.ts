// :snippet-start: runs-geturl-after-js
// :codegroup-tab: After
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
const run = await client.readRun(runId);
const response = await client.runs.getURL(run.id, {
  project_id: run.session_id!,
  trace_id: run.trace_id!,
  start_time: String(run.start_time!), // Optional, but speeds up retrieval
});
console.log(response.url);
// :snippet-end:

// :remove-start:
console.log("✓ runs-geturl-after validated");
// :remove-end:
