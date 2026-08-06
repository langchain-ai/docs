// :snippet-start: tools-pass-tools-js
import { createDeepAgent } from "deepagents";

// :remove-start:
async function search(query: string): Promise<string> {
  return query;
}

async function fetchUrl(url: string): Promise<string> {
  return url;
}

async function runQuery(sql: string): Promise<string> {
  return sql;
}
// :remove-end:

const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [search, fetchUrl, runQuery],
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
// :remove-end:
