
// :snippet-start: threads-query-list-all-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
const threads = await client.listThreads({ projectName: "default" });
for (const thread of threads) {
  console.log(thread.thread_id, thread.count);
  // :remove-start:
  break;
  // :remove-end:
}
// :snippet-end:
