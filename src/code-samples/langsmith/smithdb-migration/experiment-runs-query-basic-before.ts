// :snippet-start: experiment-runs-query-basic-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

// :remove-start:
const datasetId = "00000000-0000-0000-0000-000000000000";
const experimentId = "00000000-0000-0000-0000-000000000001";
// :remove-end:
const client = new Client();
// :remove-start:
if (false) {
// :remove-end:
const examplesWithRuns = await client.datasets.runs.query(datasetId, {
  session_ids: [experimentId],
  limit: 20,
  preview: true,
});
// :remove-start:
}
// :remove-end:
// :snippet-end:
