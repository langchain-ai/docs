// :remove-start:
process.env.ANTHROPIC_API_KEY ??= "test-key";
// :remove-end:

// :snippet-start: langgraph-graph-api-nodes-retry-custom-js
import { DatabaseSync } from "node:sqlite";
import { ChatAnthropic } from "@langchain/anthropic";
import { AIMessage } from "@langchain/core/messages";
import {
  END,
  GraphNode,
  MessagesValue,
  START,
  StateGraph,
  StateSchema,
} from "@langchain/langgraph";

const State = new StateSchema({
  messages: MessagesValue,
});

// Create an in-memory database
const db = new DatabaseSync(":memory:");

const model = new ChatAnthropic({ model: "claude-haiku-4-5-20251001" });

const callModel: GraphNode<typeof State> = async (state) => {
  const response = await model.invoke(state.messages);
  return { messages: [response] };
};

const queryDatabase: GraphNode<typeof State> = async (_state) => {
  const queryResult: string = JSON.stringify(
    db.prepare("SELECT * FROM Artist LIMIT 10;").all(),
  );

  return { messages: [new AIMessage({ content: queryResult })] };
};

const workflow = new StateGraph(State)
  .addNode("call_model", callModel, { retryPolicy: { maxAttempts: 5 } })
  .addNode("query_database", queryDatabase, {
    retryPolicy: {
      retryOn: (e: unknown): boolean => {
        if (
          e &&
          typeof e === "object" &&
          "code" in e &&
          (e as { code: string }).code === "ERR_SQLITE_ERROR"
        ) {
          // Retry on SQLite runtime errors (for example, a locked database)
          return true;
        }
        return false; // Do not retry on other errors
      },
    },
  })
  .addEdge(START, "call_model")
  .addEdge("call_model", "query_database")
  .addEdge("query_database", END);

const graph = workflow.compile();
// :snippet-end:

// :remove-start:
// Construction only: do not invoke the graph, which would call the model.
if (!("call_model" in graph.nodes) || !("query_database" in graph.nodes)) {
  throw new Error("expected call_model and query_database nodes");
}
console.log("✓ langgraph-graph-api-nodes-retry-custom-js validated");
// :remove-end:
