// :snippet-start: experiment-runs-query-pagination-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

// :remove-start:
const datasetId = "00000000-0000-0000-0000-000000000000";
const experimentId = "00000000-0000-0000-0000-000000000001";
// :remove-end:
const client = new Client();
// :remove-start:
if (false) {
// :remove-end:
for await (const run of client.datasets.experimentRuns.query(datasetId, {
  experiment_ids: [experimentId],
  page_size: 20,
})) {
  // :remove-start:
  void run;
  // :remove-end:
}
// :remove-start:
}
// :remove-end:
// :snippet-end:
