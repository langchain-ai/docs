// :snippet-start: runs-add-to-queue-after-js
// :codegroup-tab: After
// :remove-start:
import { uuid7 } from "langsmith";
// :remove-end:
import { Client } from "langsmith";

const client = new Client();
let queueId = "<queue-id>";
let projectId = "<project-id>";
// :remove-start:
projectId = (await client.readProject({ projectName: "default" })).id;
const queue = await client.createAnnotationQueue({
  name: `docs-smithdb-migration-${uuid7()}`,
});
queueId = queue.id;
// :remove-end:
const page = await client.runs.query({
  project_ids: [projectId],
  min_start_time: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  selects: ["ID", "PROJECT_ID", "START_TIME"],
  page_size: 5,
});
const runs = page.items ?? [];
// :remove-start:
if (runs.length === 0) {
  throw new Error("expected at least one run in the 'default' project");
}
// :remove-end:
await client.annotationQueues.items.create(queueId, {
  items: runs.map((run) => ({
    item_type: "RUN" as const,
    run_id: run.id,
    project_id: run.project_id!,
    start_time: run.start_time!,
  })),
});
// :snippet-end:

// :remove-start:
console.log("✓ runs-add-to-queue-after validated");
// :remove-end:
