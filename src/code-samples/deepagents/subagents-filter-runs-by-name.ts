// :snippet-start: subagents-filter-runs-by-name-js
import { Client } from "langsmith";

const client = new Client();

const runs = client.listRuns({
  projectName: "<environment-tracer-session-name>",
  filter: 'has(metadata, \'{"lc_agent_name": "research-agent"}\')',
});
// :snippet-end:

// :remove-start:
if (!client) throw new Error("expected Client");
if (!runs) throw new Error("expected listRuns iterator");
console.log("✓ subagents-filter-runs-by-name validated");
// :remove-end:
