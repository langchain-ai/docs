
// :snippet-start: runs-query-filter-errors-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
const project = await client.projects
  .list({ name: "default", limit: 1 })
  .then((page) => page.getPaginatedItems()[0]);
const runs = client.runs.query({
  project_ids: [project.id],
  has_error: true,
});
// :snippet-end:
