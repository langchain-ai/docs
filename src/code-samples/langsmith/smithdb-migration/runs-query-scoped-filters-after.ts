
// :snippet-start: runs-query-scoped-filters-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
const project = await client.projects
  .list({ name: "default", limit: 1 })
  .then((page) => page.getPaginatedItems()[0]);
const runs = client.runs.query({
  project_ids: [project.id],
  filter: 'eq(name, "RetrieveDocs")',
  trace_filter: 'and(eq(feedback_key, "user_score"), eq(feedback_score, 1))',
  tree_filter: 'eq(name, "ExpandQuery")',
});
// :snippet-end:
