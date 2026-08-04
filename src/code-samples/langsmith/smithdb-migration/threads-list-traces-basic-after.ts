
async function findThreadId(projectId: string): Promise<string> {
  const { Client } = await import("langsmith");
  const client = new Client();
  for await (const thread of client.threads.query({
    project_id: projectId,
    min_start_time: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    max_start_time: new Date().toISOString(),
    page_size: 1,
  })) {
    return thread.thread_id!;
  }
  throw new Error("no threads found");
}

// :snippet-start: threads-list-traces-basic-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
const project = await client.readProject({ projectName: "default" });
let threadId = "<thread-id>";
// :remove-start:
threadId = await findThreadId(project.id);
// :remove-end:
for await (const trace of client.threads.listTraces(threadId, {
  project_id: project.id,
  selects: ["TRACE_ID", "START_TIME"],
})) {
  console.log(trace.trace_id, trace.start_time);
  // :remove-start:
  break;
  // :remove-end:
}
// :snippet-end:
