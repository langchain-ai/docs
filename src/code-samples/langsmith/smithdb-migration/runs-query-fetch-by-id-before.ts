
// :snippet-start: runs-query-fetch-by-id-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
const runs = client.listRuns({ id: ["<run-id-1>", "<run-id-2>"] });
// :snippet-end:
