// :snippet-start: experiment-runs-query-basic-after-js
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
const page = await client.datasets.experimentRuns.create(datasetId, {
  experiment_ids: [experimentId],
  page_size: 20,
  selects: ["ID", "NAME", "STATUS", "INPUTS_PREVIEW", "OUTPUTS_PREVIEW"],
});
const examplesWithRuns = page.getPaginatedItems();
// :remove-start:
}
// :remove-end:
// :snippet-end:
