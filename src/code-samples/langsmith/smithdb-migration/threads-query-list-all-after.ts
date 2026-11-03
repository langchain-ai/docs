
// :snippet-start: threads-query-list-all-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
const project = await client.readProject({ projectName: "default" });
for await (const thread of client.threads.query({
  project_id: project.id,
  min_start_time: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  max_start_time: new Date().toISOString(),
})) {
  console.log(thread.thread_id, thread.count);
  // :remove-start:
  break;
  // :remove-end:
}
// :snippet-end:
