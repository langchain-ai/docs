// :snippet-start: runs-geturl-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
let runId = "<run-id>";
let projectId = "<project-id>";
// :remove-start:
projectId = (await client.readProject({ projectName: "default" })).id;
const found = await client.runs.query({
  project_ids: [projectId],
  min_start_time: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  page_size: 1,
});
if (!found.items?.length) {
  throw new Error("expected at least one run in the 'default' project");
}
runId = found.items[0].id!;
// :remove-end:
const run = await client.runs.retrieve(runId, {
  project_id: projectId,
  selects: ["ID", "PROJECT_ID", "TRACE_ID", "START_TIME"],
});
const response = await client.runs.getURL(run.id!, {
  project_id: run.project_id!,
  trace_id: run.trace_id!,
  start_time: run.start_time!, // Optional, but speeds up retrieval
});
console.log(response.url);
// :snippet-end:

// :remove-start:
console.log("✓ runs-geturl-after validated");
// :remove-end:
