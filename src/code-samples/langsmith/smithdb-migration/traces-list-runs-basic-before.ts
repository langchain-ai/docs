
// :snippet-start: traces-list-runs-basic-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
const project = await client.readProject({ projectName: "default" });
let traceId = "<trace-id>";
// :remove-start:
for await (const run of client.listRuns({ projectId: project.id, isRoot: true, limit: 1 })) {
  traceId = run.trace_id!;
  break;
}
// :remove-end:
const runs = [];
for await (const run of client.listRuns({ projectId: project.id, traceId })) {
  runs.push(run);
}
for (const run of runs) {
  console.log(run.name, run.run_type, run.status);
}
// :snippet-end:
