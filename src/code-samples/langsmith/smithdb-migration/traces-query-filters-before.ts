
// :snippet-start: traces-query-filters-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
const project = await client.readProject({ projectName: "default" });

// v1 has no root-run-only filter concept — isRoot plus a regular filter is
// the closest equivalent, still scanning every run to match.
for await (const run of client.listRuns({
  projectId: project.id,
  isRoot: true,
  filter: 'eq(status, "error")',
  limit: 5,
})) {
  console.log(run.trace_id);
}
// :snippet-end:
