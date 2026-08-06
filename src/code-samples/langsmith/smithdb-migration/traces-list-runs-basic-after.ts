
// :snippet-start: traces-list-runs-basic-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
const project = await client.readProject({ projectName: "default" });
let traceId = "<trace-id>";
// :remove-start:
for await (const t of client.traces.query({
  project_id: project.id,
  min_start_time: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  max_start_time: new Date().toISOString(),
})) {
  traceId = t.root_run!.trace_id!;
  break;
}
// :remove-end:
const response = await client.traces.listRuns(traceId, {
  project_id: project.id,
  selects: ["NAME", "RUN_TYPE", "STATUS"],
});
for (const run of response.items ?? []) {
  console.log(run.name, run.run_type, run.status);
}
// :snippet-end:
