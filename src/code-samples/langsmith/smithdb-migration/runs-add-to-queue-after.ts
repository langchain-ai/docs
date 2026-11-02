// :snippet-start: runs-add-to-queue-after-js
// :codegroup-tab: After
import { uuid7 } from "langsmith";
import { Client } from "langsmith";

const client = new Client();
let queueId = "<queue-id>";
const runs = [];
for await (const run of client.listRuns({ projectName: "default", limit: 5 })) {
  runs.push(run);
}
// :remove-start:
const queue = await client.createAnnotationQueue({
  name: `docs-smithdb-migration-${uuid7()}`,
});
queueId = queue.id;
if (runs.length === 0) {
  throw new Error("expected at least one run in the 'default' project");
}
// :remove-end:
await client.annotationQueues.items.create(queueId, {
  items: runs.map((run) => ({
    item_type: "RUN" as const,
    run_id: run.id,
    project_id: run.session_id!,
    start_time: new Date(run.start_time).toISOString(),
  })),
});
// :snippet-end:

// :remove-start:
console.log("✓ runs-add-to-queue-after validated");
// :remove-end:
