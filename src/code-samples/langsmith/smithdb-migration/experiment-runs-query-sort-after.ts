// :snippet-start: experiment-runs-query-sort-after-js
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
const page = await client.datasets.experimentRuns.query(datasetId, {
  experiment_ids: [experimentId],
  sort: { by: "feedback.correctness", order: "ASC" },
});
// :remove-start:
}
// :remove-end:
// :snippet-end:
