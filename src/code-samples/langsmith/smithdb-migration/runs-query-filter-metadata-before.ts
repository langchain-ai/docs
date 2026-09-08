
// :snippet-start: runs-query-filter-metadata-before-js
// :codegroup-tab: Before
import { Client } from "langsmith";

const client = new Client();
const filterStr = 'and(eq(metadata_key, "user_id"), eq(metadata_value, "u_123"))';
const runs = client.listRuns({ projectName: "default", filter: filterStr });
// :snippet-end:
