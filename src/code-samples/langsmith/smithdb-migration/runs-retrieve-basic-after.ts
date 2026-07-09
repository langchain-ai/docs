import { Client } from "langsmith";

async function findRun(projectId: string) {
  const client = new Client();
  for await (const run of client.runs.query({ project_ids: [projectId], selects: ["ID", "START_TIME"] })) {
    return run;
  }
  return null;
}

async function getProjectId() {
  const client = new Client();
  const project = await client.readProject({ projectName: "default" });
  return project.id;
}

// :snippet-start: runs-retrieve-basic-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
let runId = "<run-id>";
let startTime = "2026-06-01T12:00:00Z";
let projectId = "<project-id>";
// :remove-start:
projectId = await getProjectId();
const run = await findRun(projectId);
runId = run.id;
startTime = run.start_time;
// :remove-end:
const retrievedRun = await client.runs.retrieve(runId, {
  project_id: projectId,
  start_time: startTime,
  selects: ["NAME", "STATUS", "TOTAL_TOKENS"],
});
console.log(retrievedRun.name, retrievedRun.status, retrievedRun.total_tokens);
// :snippet-end:
