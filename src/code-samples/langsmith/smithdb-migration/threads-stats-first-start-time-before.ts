
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

// :snippet-start: threads-stats-first-start-time-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
const project = await client.readProject({ projectName: "default" });
let threadId = "<thread-id>";
// :remove-start:
threadId = await findThreadId(project.id);
// :remove-end:
const threadFilter = `eq(thread_id, "${threadId}")`;
const stats = await client.getRunStats({
  projectIds: [project.id],
  filter: threadFilter,
  isRoot: true,
});
// getRunStats has no "first_start_time" field — a second call, sorted
// ascending, is needed to find the thread's earliest run.
let firstRun;
for await (const run of client.listRuns({
  projectId: project.id,
  filter: threadFilter,
  isRoot: true,
  order: "asc",
  limit: 1,
})) {
  firstRun = run;
  break;
}
console.log(stats.run_count, firstRun?.start_time);
// :snippet-end:
