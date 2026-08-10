// :remove-start:
import { getCurrentRunTree, traceable } from "langsmith/traceable";

process.env.LANGSMITH_TRACING = "true";

// The `default` project holds no nested traces of its own, so the sample
// creates one instead of depending on data it does not control.
const seeded: { runId?: string } = {};

const leaf = traceable(async (index: number) => `leaf ${index}`, {
  name: "leaf",
  run_type: "llm",
});
const branch = traceable(
  async () => {
    await leaf(0);
    return "branch";
  },
  { name: "branch" },
);
const seedRoot = traceable(
  async () => {
    seeded.runId = getCurrentRunTree().id;
    await leaf(1);
    await branch();
    return "root";
  },
  { name: "docs-child-runs-example", project_name: "default" },
);
// :remove-end:

// :snippet-start: runs-retrieve-child-runs-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
let runId = "<run-id>";
// :remove-start:
await seedRoot();
await client.awaitPendingTraceBatches();
runId = seeded.runId!;
// The v1 read path becomes consistent a moment after ingestion, so poll until
// it returns the full child tree.
for (let attempt = 0; attempt < 30; attempt += 1) {
  try {
    const seededRun = await client.readRun(runId, { loadChildRuns: true });
    if ((seededRun.child_runs ?? []).length === 2) break;
  } catch {
    // Not ingested yet.
  }
  await new Promise((resolve) => setTimeout(resolve, 2000));
}
// :remove-end:

const run = await client.readRun(runId, { loadChildRuns: true });

// `child_runs` holds the direct children, each with its own nested `child_runs`.
// `child_run_ids` holds every descendant, at any depth.
for (const child of run.child_runs ?? []) {
  console.log(child.name, child.run_type, (child.child_runs ?? []).length);
}
console.log((run.child_run_ids ?? []).length, "descendants");
// :snippet-end:

// :remove-start:
if ((run.child_runs ?? []).length !== 2) {
  throw new Error(`expected 2 direct children, got ${(run.child_runs ?? []).length}`);
}
if ((run.child_run_ids ?? []).length !== 3) {
  throw new Error(`expected 3 descendants, got ${(run.child_run_ids ?? []).length}`);
}
console.log("✓ runs-retrieve-child-runs-before validated");
// :remove-end:
