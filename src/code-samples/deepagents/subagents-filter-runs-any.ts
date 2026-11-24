// :remove-start:
import { Client } from "langsmith";

const client = new Client();
// :remove-end:

// :snippet-start: subagents-filter-runs-any-js
const runs = client.listRuns({
  projectName: "<environment-tracer-session-name>",
  filter: "has(metadata, 'lc_agent_name')",
});
// :snippet-end:

// :remove-start:
if (!runs) throw new Error("expected listRuns iterator");
console.log("✓ subagents-filter-runs-any validated");
// :remove-end:
