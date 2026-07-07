import { Client } from "langsmith";

async function findRun(projectId: string) {
  const client = new Client();
  for await (const run of client.runs.query({ project_ids: [projectId], selects: ["ID", "START_TIME"] })) {
    return run;
  }
  return null;
}

// :snippet-start: runs-retrieve-by-id-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
const projectPage = await client.projects.list({ name: "default", limit: 1 });
const project = projectPage.getPaginatedItems()[0];
let runId = "<run-id>";
let startTime = "2026-06-01T12:00:00Z";
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
