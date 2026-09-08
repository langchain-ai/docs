// :snippet-start: runs-retrieve-not-found-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
let runId = "<run-id>";
// :remove-start:
runId = crypto.randomUUID();
// :remove-end:

try {
  await client.readRun(runId);
} catch (e: any) {
  if (e?.status === 404) {
    console.log(`Run ${runId} not found`);
  }
  // :remove-start:
  else {
    throw e;
  }
  // :remove-end:
}
// :snippet-end:
