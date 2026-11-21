// :snippet-start: runs-list-from-queue-before-js
// :codegroup-tab: Before
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
const { size } = await client.getSizeFromAnnotationQueue(queueId);
console.log(size);

for await (const run of client.listRunsFromAnnotationQueue(queueId, {
  status: "needs_my_review",
})) {
  console.log(run.name, run.status);
  // :remove-start:
  names.push(run.name);
  // :remove-end:
}

const firstRun = await client.getRunFromAnnotationQueue(queueId, 0);
// :snippet-end:

// :remove-start:
if (size !== 1) throw new Error(`expected size 1, got ${size}`);
if (names.length !== 1) throw new Error(`expected 1 run, got ${names.length}`);
if (firstRun.id !== seedRuns[0].id) throw new Error("index 0 returned a different run");
console.log("✓ runs-list-from-queue-before validated");
// :remove-end:
