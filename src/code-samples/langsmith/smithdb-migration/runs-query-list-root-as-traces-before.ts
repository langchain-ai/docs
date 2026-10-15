
// :snippet-start: runs-query-list-root-as-traces-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
const project = await client.readProject({ projectName: "default" });

for await (const run of client.listRuns({ projectId: project.id, isRoot: true, limit: 5 })) {
  console.log(run.trace_id, run.name);
}
// :snippet-end:
