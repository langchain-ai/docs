
// :snippet-start: threads-query-filter-status-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
const threads = await client.listThreads({
  projectName: "default",
  filter: 'eq(status, "error")',
});
for (const thread of threads) {
  console.log(thread.thread_id, thread.last_error);
  // :remove-start:
  break;
  // :remove-end:
}
// :snippet-end:
