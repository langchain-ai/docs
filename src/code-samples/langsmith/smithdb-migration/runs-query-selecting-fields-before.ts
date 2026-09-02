
// :snippet-start: runs-query-selecting-fields-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
// returns a default set of fields; no explicit selection needed
const runs = client.listRuns({ projectName: "default" });
for await (const run of runs) {
  console.log(run.id, run.name, run.run_type, run.status, run.start_time, run.inputs, run.error);
  // :remove-start:
  break;
  // :remove-end:
}
// :snippet-end:
