
// :snippet-start: runs-query-filter-root-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
const project = await client.readProject({ projectName: "default" });
const runs = client.runs.query({
  project_ids: [project.id],
  is_root: true,
});
// :snippet-end:
