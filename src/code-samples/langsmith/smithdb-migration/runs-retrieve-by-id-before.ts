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

// :snippet-start: runs-retrieve-by-id-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
let runId = "<run-id>";
// :remove-start:
const projectId = await getProjectId();
const run = await findRun(projectId);
runId = run.id;
// :remove-end:
await client.readRun(runId);
// :snippet-end:
