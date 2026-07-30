
async function findThreadId(projectId: string): Promise<string> {
  const { Client } = await import("langsmith");
  const client = new Client();
  for await (const thread of client.threads.query({
    project_id: projectId,
    min_start_time: "2026-07-01T00:00:00Z",
    max_start_time: "2026-07-31T23:59:59Z",
    page_size: 1,
  })) {
    return thread.thread_id!;
  }
  throw new Error("no threads found");
}

// :snippet-start: threads-list-traces-selecting-fields-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
let threadId = "<thread-id>";
// :remove-start:
const project = await client.readProject({ projectName: "default" });
threadId = await findThreadId(project.id);
// :remove-end:
for await (const run of client.readThread({
  threadId,
  projectName: "default",
  select: ["id", "total_tokens", "total_cost"],
})) {
  console.log(run.id, run.total_tokens, run.total_cost);
  // :remove-start:
  break;
  // :remove-end:
}
// :snippet-end:
