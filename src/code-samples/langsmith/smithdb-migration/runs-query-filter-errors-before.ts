
// :snippet-start: runs-query-filter-errors-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
const runs = client.listRuns({ projectName: "default", error: true });
// :snippet-end:
