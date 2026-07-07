
// :snippet-start: runs-query-boolean-filters-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
const filterStr =
  'and(gt(start_time, "2023-07-15T12:34:56Z"),' +
  ' or(neq(status, "error"),' +
  '    and(eq(feedback_key, "Correctness"), eq(feedback_score, 0.0))))';
const runs = client.listRuns({ projectName: "default", filter: filterStr });
// :snippet-end:
