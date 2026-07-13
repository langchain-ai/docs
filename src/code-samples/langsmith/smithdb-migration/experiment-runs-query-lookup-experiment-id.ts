// :snippet-start: experiment-runs-query-lookup-experiment-id-js
import { Client } from "langsmith";

const client = new Client();
// :remove-start:
if (false) {
// :remove-end:
const experimentId = (await client.readProject({ projectName: "my-experiment" })).id;
// :remove-start:
void experimentId;
}
// :remove-end:
// :snippet-end:
