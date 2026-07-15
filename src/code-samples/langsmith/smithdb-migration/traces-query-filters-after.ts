
// :snippet-start: traces-query-filters-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
const project = await client.readProject({ projectName: "default" });

// trace_filter is implicitly root-run-only — no is_root needed.
let count = 0;
for await (const trace of client.traces.query({
  project_id: project.id,
  min_start_time: "2026-07-01T00:00:00Z",
  max_start_time: "2026-07-31T23:59:59Z",
  trace_filter: 'eq(status, "error")',
})) {
  console.log(trace.root_run?.trace_id);
  count += 1;
  if (count >= 5) break;
}

// trace_ids is a fast-path when you already know which traces you want.
let traceId = "<trace-id>";
// :remove-start:
for await (const t of client.traces.query({
  project_id: project.id,
  min_start_time: "2026-07-01T00:00:00Z",
  max_start_time: "2026-07-31T23:59:59Z",
  page_size: 1,
})) {
  traceId = t.root_run!.trace_id!;
  break;
}
// :remove-end:
for await (const trace of client.traces.query({
  project_id: project.id,
  min_start_time: "2026-07-01T00:00:00Z",
  max_start_time: "2026-07-31T23:59:59Z",
  trace_ids: [traceId],
})) {
  console.log(trace.root_run?.trace_id);
}
// :snippet-end:
