// :remove-start:
import { getCurrentRunTree, traceable } from "langsmith/traceable";

process.env.LANGSMITH_TRACING = "true";

// The `default` project holds no nested traces of its own, so the sample
// creates one instead of depending on data it does not control.
const seeded: { traceId?: string } = {};

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
    seeded.traceId = getCurrentRunTree().trace_id;
    await leaf(1);
    await branch();
    return "root";
  },
  { name: "docs-child-runs-example", project_name: "default" },
);
// :remove-end:

// :snippet-start: runs-retrieve-child-runs-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
const project = await client.readProject({ projectName: "default" });
// A root run is its own trace, so `traceId` is also the run ID.
let traceId = "<trace-id>";
// :remove-start:
await seedRoot();
await client.awaitPendingTraceBatches();
traceId = seeded.traceId!;
// The v2 read path becomes consistent a moment after ingestion, so poll until
// the whole trace is visible.
for (let attempt = 0; attempt < 30; attempt += 1) {
  const seededTrace = await client.traces.listRuns(traceId, {
    project_id: project.id,
    selects: ["ID"],
  });
  if ((seededTrace.items ?? []).length === 4) break;
  await new Promise((resolve) => setTimeout(resolve, 2000));
}
// :remove-end:

const traceRuns = await client.traces.listRuns(traceId, {
  project_id: project.id,
  selects: ["ID", "NAME", "RUN_TYPE", "PARENT_RUN_IDS", "START_TIME", "END_TIME"],
});

// `parent_run_ids` is the full ancestor chain, root first, closest parent last.
// A run is a descendant of any ID in that chain, at any depth, not only of the
// immediate parent. This flat list replaces `child_run_ids`.
const descendants = (traceRuns.items ?? []).filter((traceRun) =>
  (traceRun.parent_run_ids ?? []).includes(traceId),
);
console.log(descendants.length, "descendants");

// Optional: group the runs by immediate parent to walk the trace as a tree,
// which is the information `child_runs` used to carry.
type TraceRun = NonNullable<typeof traceRuns.items>[number];
const byParent = new Map<string, TraceRun[]>();
for (const traceRun of traceRuns.items ?? []) {
  const ancestors = traceRun.parent_run_ids ?? [];
  if (ancestors.length === 0) continue;
  // The last ancestor is the immediate parent.
  const parentId = ancestors[ancestors.length - 1];
  byParent.set(parentId, [...(byParent.get(parentId) ?? []), traceRun]);
}

const children = byParent.get(traceId) ?? [];
for (const child of children) {
  console.log(child.name, child.run_type, (byParent.get(child.id!) ?? []).length);
}
// :snippet-end:

// :remove-start:
if (children.length !== 2) {
  throw new Error(`expected 2 direct children, got ${children.length}`);
}
if (descendants.length !== 3) {
  throw new Error(`expected 3 descendants, got ${descendants.length}`);
}
console.log("✓ runs-retrieve-child-runs-after validated");
// :remove-end:
