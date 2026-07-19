// :snippet-start: experiment-runs-query-sort-after-js
// :codegroup-tab: After
import { Client } from "langsmith";

const client = new Client();
// :remove-start:
const DATASET_NAME = "docs-experiment-runs-query-fixture";
const EXPERIMENT_NAME = "docs-experiment-runs-query-fixture-experiment";

if (!(await client.hasDataset({ datasetName: DATASET_NAME }))) {
  const newDataset = await client.createDataset(DATASET_NAME);
  await client.createExamples([
    { inputs: { question: "2 + 2" }, outputs: { answer: "4" }, dataset_id: newDataset.id },
    { inputs: { question: "3 + 3" }, outputs: { answer: "6" }, dataset_id: newDataset.id },
    { inputs: { question: "4 + 4" }, outputs: { answer: "9" }, dataset_id: newDataset.id },
  ]);
}
const dataset = await client.readDataset({ datasetName: DATASET_NAME });
const datasetId = dataset.id;

// The experiment is shared across every experiment-runs-query sample (this
// file and its siblings): created once, ever, and reused afterward so the
// suite doesn't spend a real evaluation run per file.
if (!(await client.hasProject({ projectName: EXPERIMENT_NAME }))) {
  await client.createProject({
    projectName: EXPERIMENT_NAME,
    referenceDatasetId: datasetId,
  });
  for await (const example of client.listExamples({ datasetId })) {
    const [a, b] = (example.inputs.question as string).split(" + ").map(Number);
    const answer = String(a + b);
    const runId = crypto.randomUUID();
    const now = new Date().toISOString();
    await client.createRun({
      id: runId,
      name: "target",
      run_type: "chain",
      inputs: example.inputs,
      outputs: { answer },
      reference_example_id: example.id,
      project_name: EXPERIMENT_NAME,
      start_time: now,
      end_time: now,
    });
    const score = answer === (example.outputs?.answer as string) ? 1 : 0;
    await client.createFeedback(runId, "correctness", { score });
  }
  // Sorting queries derive their time window from the experiment's start
  // time, truncated to whole seconds server-side. A short buffer avoids a
  // same-second min/max window on whichever run performs this creation.
  await new Promise((resolve) => setTimeout(resolve, 1000));
}
const experimentName = EXPERIMENT_NAME;
// :remove-end:
const experimentId = (await client.readProject({ projectName: experimentName })).id;
const page = await client.datasets.experimentRuns.query(datasetId, {
  experiment_ids: [experimentId],
  sort: { by: "feedback.correctness", order: "ASC" },
});
// :remove-start:
void page;
// :remove-end:
// :snippet-end:
