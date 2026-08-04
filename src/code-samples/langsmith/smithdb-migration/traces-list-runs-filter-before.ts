
// :snippet-start: traces-list-runs-filter-before-js
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
const llmRuns = [];
for await (const run of client.listRuns({
  projectId: project.id,
  traceId,
  filter: 'eq(run_type, "llm")',
})) {
  llmRuns.push(run);
}
// :snippet-end:
