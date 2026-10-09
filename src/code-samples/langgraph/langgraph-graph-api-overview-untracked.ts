// :remove-start:
interface DatabaseConnection {
  query: (sql: string) => string;
}
// :remove-end:
// :snippet-start: langgraph-graph-api-overview-untracked-js
import { StateSchema, UntrackedValue, MessagesValue } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  messages: MessagesValue,
  dbConnection: new UntrackedValue<DatabaseConnection>(),
  tempCache: new UntrackedValue(z.record(z.string(), z.unknown()), { guard: false }),
});
// :snippet-end:

// :remove-start:
import { END, START, StateGraph } from "@langchain/langgraph";

const graph = new StateGraph(State)
  .addNode("use", (state) => ({
    tempCache: { result: state.dbConnection.query("select 1") },
  }))
  .addEdge(START, "use")
  .addEdge("use", END)
  .compile();

const result = await graph.invoke({
  messages: [],
  dbConnection: { query: () => "one" },
  tempCache: {},
});
if (result.tempCache.result !== "one") {
  throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
}
console.log("✓ langgraph-graph-api-overview-untracked-js");
// :remove-end:
