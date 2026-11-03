
// :snippet-start: runs-query-filter-root-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
const runs = client.listRuns({ projectName: "default", isRoot: true });
// :snippet-end:
