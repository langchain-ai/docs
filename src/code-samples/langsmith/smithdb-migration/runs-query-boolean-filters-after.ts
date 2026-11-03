
// :snippet-start: runs-query-boolean-filters-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
const filterStr =
  'and(gt(start_time, "2023-07-15T12:34:56Z"),' +
  ' or(eq(status, "error"), eq(run_type, "llm")))';
const project = await client.readProject({ projectName: "default" });
const runs = client.runs.query({
  project_ids: [project.id],
  filter: filterStr,
});
// :snippet-end:
