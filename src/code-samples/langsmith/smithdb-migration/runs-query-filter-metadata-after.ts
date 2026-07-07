
// :snippet-start: runs-query-filter-metadata-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
const filterStr = 'and(eq(metadata_key, "user_id"), eq(metadata_value, "u_123"))';
const project = await client.projects
  .list({ name: "default", limit: 1 })
  .then((page) => page.getPaginatedItems()[0]);
const runs = client.runs.query({
  project_ids: [project.id],
  filter: filterStr,
});
// :snippet-end:
