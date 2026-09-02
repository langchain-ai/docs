
// :snippet-start: runs-query-filter-time-range-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
const runs = client.listRuns({
  projectName: "default",
  startTime: new Date(Date.now() - 24 * 60 * 60 * 1000),
  runType: "llm",
});
// :snippet-end:
