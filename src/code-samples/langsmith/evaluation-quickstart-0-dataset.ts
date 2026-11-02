// Evaluation quickstart, step 3: create the sample dataset.
// Runs before the evaluation-quickstart-*-eval-*.ts files (lexical order
// within the "evaluation-quickstart" serial group).

// :remove-start:
import { Client as SetupClient } from "langsmith";

// createDataset fails on a name that already exists; start each run clean.
const setupClient = new SetupClient();
if (await setupClient.hasDataset({ datasetName: "Sample dataset" })) {
  await setupClient.deleteDataset({ datasetName: "Sample dataset" });
}
// :remove-end:

// :snippet-start: evaluation-quickstart-dataset-js
// :codegroup-tab: TypeScript
// dataset.ts
import { Client } from "langsmith";

async function main() {
const client = new Client();

const dataset = await client.createDataset(
    "Sample dataset",
    { description: "A sample dataset in LangSmith." }
);

// Define examples
const inputs = [
    { question: "Which country is Mount Kilimanjaro located in?" },
    { question: "What is Earth's lowest point?" },
];
const outputs = [
    { answer: "Mount Kilimanjaro is located in Tanzania." },
    { answer: "Earth's lowest point is The Dead Sea." },
];

await client.createExamples({
    datasetId: dataset.id,
    inputs,
    outputs,
});

console.log("Created dataset:", dataset.name);
}

main().catch((e) => {
    console.error(e);
    process.exit(1);
});
// :snippet-end:
