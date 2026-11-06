// :snippet-start: runs-list-from-queue-after-js
// :codegroup-tab: After
// :remove-start:
import { uuid7 } from "langsmith";
// :remove-end:
import { Client } from "langsmith";

const client = new Client();
let queueId = "<queue-id>";
// :remove-start:
const queue = await client.createAnnotationQueue({
  name: `docs-smithdb-migration-${uuid7()}`,
});
queueId = queue.id;
const seedRuns = [];
for await (const run of client.listRuns({ projectName: "default", limit: 1 })) {
  seedRuns.push(run);
}
if (seedRuns.length === 0) {
  throw new Error("expected at least one run in the 'default' project");
}
await client.addRunsToAnnotationQueue(queueId, [seedRuns[0].id]);
const names: string[] = [];
// :remove-end:
const { count } = await client.annotationQueues.items.retrieveCount(queueId, {
  status: "needs_my_review",
});
console.log(count);

// Items carry the run's lookup keys, not its contents.
for await (const item of client.annotationQueues.items.list(queueId, {
  status: "needs_my_review",
  item_type: "RUN",
})) {
  const run = await client.runs.retrieveV2(item.run_id!, {
    project_id: item.project_id!,
    start_time: item.start_time,
    selects: ["NAME", "STATUS", "INPUTS", "OUTPUTS"],
  });
  console.log(run.name, run.status);
  // :remove-start:
  names.push(run.name ?? "");
  // :remove-end:
}
// :snippet-end:

// :remove-start:
if (count !== 1) throw new Error(`expected count 1, got ${count}`);
if (names.length !== 1 || !names[0]) {
  throw new Error(`expected 1 named run, got ${JSON.stringify(names)}`);
}
console.log("✓ runs-list-from-queue-after validated");
// :remove-end:
