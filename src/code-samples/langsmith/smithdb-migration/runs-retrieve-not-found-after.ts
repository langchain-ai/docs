// :snippet-start: runs-retrieve-not-found-after-js
// :codegroup-tab: After
import { Client, NotFoundError } from "langsmith";

const client = new Client();
const project = await client.readProject({ projectName: "default" });
let runId = "<run-id>";
const startTime = "2026-06-01T12:00:00Z";
// :remove-start:
runId = crypto.randomUUID();
// :remove-end:

try {
  await client.runs.retrieve(runId, {
    project_id: project.id,
    start_time: startTime,
  });
} catch (e) {
  if (e instanceof NotFoundError) {
    console.log(`Run ${runId} not found`);
  }
  // :remove-start:
  else {
    throw e;
  }
  // :remove-end:
}
// :snippet-end:
