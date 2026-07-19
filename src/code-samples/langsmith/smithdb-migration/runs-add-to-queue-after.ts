// :snippet-start: runs-add-to-queue-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
let queueId = "<queue-id>";
const runs = [];
for await (const run of client.listRuns({ projectName: "default", limit: 5 })) {
  runs.push(run);
}
// :remove-start:
const queue = await client.createAnnotationQueue({
  name: `docs-smithdb-migration-${crypto.randomUUID()}`,
});
queueId = queue.id;
if (runs.length === 0) {
  throw new Error("expected at least one run in the 'default' project");
}
// :remove-end:
await client.addRunsToAnnotationQueue(
  queueId,
  runs.map((run) => ({
    runId: run.id,
    sessionId: run.session_id!,
    startTime: run.start_time!,
  })),
);
// :snippet-end:

// :remove-start:
console.log("✓ runs-add-to-queue-after validated");
// :remove-end:
