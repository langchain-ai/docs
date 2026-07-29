import { Client } from "langsmith";

async function findRun(projectId: string) {
  const client = new Client();
  const maxStart = new Date();
  const minStart = new Date(maxStart);
  minStart.setUTCMonth(minStart.getUTCMonth() - 1);
  for await (const run of client.runs.query({
    project_ids: [projectId],
    min_start_time: minStart.toISOString(),
    max_start_time: maxStart.toISOString(),
    selects: ["ID", "START_TIME"],
  })) {
    return run;
  }
  return null;
}

// :snippet-start: runs-retrieve-by-id-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
const project = await client.readProject({ projectName: "default" });
let runId = "<run-id>";
let startTime = "2026-06-01T12:00:00Z"; // Optional, but speeds up retrieval
// :remove-start:
const run = await findRun(project.id);
runId = run.id;
startTime = run.start_time;
// :remove-end:
await client.runs.retrieve(runId, {
  project_id: project.id,
  start_time: startTime,
});
// :snippet-end:
