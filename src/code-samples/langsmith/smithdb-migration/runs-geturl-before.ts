// :snippet-start: runs-geturl-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
const runs = [];
for await (const run of client.listRuns({ projectName: "default", limit: 1 })) {
  runs.push(run);
}
// :remove-start:
if (runs.length === 0) {
  throw new Error("expected at least one run in the 'default' project");
}
// :remove-end:
const run = runs[0];
const url = await client.getRunUrl({ run });
console.log(url);
// :snippet-end:

// :remove-start:
console.log("✓ runs-get-url-before validated");
// :remove-end:
