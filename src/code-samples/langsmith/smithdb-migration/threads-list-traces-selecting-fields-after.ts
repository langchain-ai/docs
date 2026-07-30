
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

// :snippet-start: threads-list-traces-selecting-fields-after-js
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
  selects: ["TRACE_ID", "TOTAL_TOKENS", "TOTAL_COST"],
})) {
  console.log(trace.trace_id, trace.total_tokens, trace.total_cost);
  // :remove-start:
  break;
  // :remove-end:
}
// :snippet-end:
