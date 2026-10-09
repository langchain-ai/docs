// :snippet-start: resolve-evaluators-js
import { Client, EvaluatorAddress } from "langsmith";

const client = new Client();
const evaluators = new EvaluatorAddress();
// :remove-start:
// Evaluator traces go to the workspace's project named "evaluators".
await client.createProject({ projectName: "evaluators", upsert: true });
// :remove-end:

const project = await client.sessions.resolve(evaluators.toApiAddress());

for await (const run of client.runs.query({
  project_ids: [project.session_id],
})) {
  console.log(run.id);
}
// :snippet-end:

// :remove-start:
console.log("✓ resolve-evaluators validated");
// :remove-end:
