// :snippet-start: experiment-runs-query-sort-after-js
// :codegroup-tab: After
import { Client } from "langsmith";
// :remove-start:
import { evaluate } from "langsmith/evaluation";
// :remove-end:

const client = new Client();
// :remove-start:
const DATASET_NAME = "docs-experiment-runs-query-fixture";
if (!(await client.hasDataset({ datasetName: DATASET_NAME }))) {
  const newDataset = await client.createDataset(DATASET_NAME);
  await client.createExamples([
    { inputs: { question: "2 + 2" }, outputs: { answer: "4" }, dataset_id: newDataset.id },
    { inputs: { question: "3 + 3" }, outputs: { answer: "6" }, dataset_id: newDataset.id },
    { inputs: { question: "4 + 4" }, outputs: { answer: "9" }, dataset_id: newDataset.id },
  ]);
}
const dataset = await client.readDataset({ datasetName: DATASET_NAME });

function target(inputs: { question: string }) {
  const [a, b] = inputs.question.split(" + ").map(Number);
  return { answer: String(a + b) };
}

function correctness({
  outputs,
  referenceOutputs,
}: {
  outputs?: Record<string, unknown>;
  referenceOutputs?: Record<string, unknown>;
}) {
  return {
    key: "correctness",
    score: outputs?.answer === referenceOutputs?.answer ? 1 : 0,
  };
}

const evalResults = await evaluate(target, {
  data: DATASET_NAME,
  evaluators: [correctness],
  experimentPrefix: "docs-experiment-runs-query-sort",
});
const datasetId = dataset.id;
const experimentName = evalResults.experimentName;
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
