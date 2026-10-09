// :snippet-start: resolve-experiment-js
import { Client, ExperimentAddress } from "langsmith";

const client = new Client();
let experimentId = "<experiment-id>";
// :remove-start:
const dataset = await client.createDataset(
  `docs-resolve-an-agent-${crypto.randomUUID().slice(0, 8)}`,
);
const seededExperiment = await client.createProject({
  projectName: `docs-resolve-an-agent-${crypto.randomUUID().slice(0, 8)}`,
  referenceDatasetId: dataset.id,
});
experimentId = seededExperiment.id;
// :remove-end:
const experiment = new ExperimentAddress(experimentId);

const project = await client.sessions.resolve(experiment.toApiAddress());

for await (const run of client.runs.query({
  project_ids: [project.session_id],
})) {
  console.log(run.id);
}
// :snippet-end:

// :remove-start:
await client.deleteProject({ projectId: experimentId });
await client.deleteDataset({ datasetId: dataset.id });
console.log("✓ resolve-experiment validated");
// :remove-end:
