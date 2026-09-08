
// :snippet-start: runs-query-list-all-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
const runs = client.listRuns({ projectName: "default" });
// :snippet-end:
