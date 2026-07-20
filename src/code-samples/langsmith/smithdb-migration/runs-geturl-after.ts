// :snippet-start: runs-geturl-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
const runs = [];
for await (const run of client.listRuns({ projectName: "default", limit: 1 })) {
  runs.push(run);
}
// :remove-start:
if (runs.length === 0) {
  throw new Error("expected at least one run in the 'default' project");
}
// :remove-end:
const run = runs[0];
const response = await client.runs.getURL(run.id, {
  project_id: run.session_id!,
  trace_id: run.trace_id!,
  start_time: String(run.start_time!),
});
console.log(response.url);
// :snippet-end:

// :remove-start:
console.log("✓ runs-get-url-after validated");
// :remove-end:
