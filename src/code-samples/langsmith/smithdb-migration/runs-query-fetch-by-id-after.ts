
// :snippet-start: runs-query-fetch-by-id-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
const project = await client.readProject({ projectName: "default" });
const runs = client.runs.query({
  project_ids: [project.id],
  ids: ["<run-id-1>", "<run-id-2>"],
});
// :snippet-end:
