// :snippet-start: graph-api-using-tasks-task-js
import { v7 as uuid7 } from "uuid";
import * as z from "zod";

import {
  END,
  MemorySaver,
  START,
  StateGraph,
  StateSchema,
  task,
} from "@langchain/langgraph";
import type { GraphNode } from "@langchain/langgraph";

const State = new StateSchema({
  urls: z.array(z.string()),
  results: z.array(z.string()).optional(),
});

const makeRequest = task("makeRequest", async (url: string) => {
  const response = await fetch(url);  // [!code highlight]
  const text = await response.text();
  return text.slice(0, 100);
});

const callApi: GraphNode<typeof State> = async (state) => {
  const pending = state.urls.map((url) => makeRequest(url));  // [!code highlight]
  const results = await Promise.all(pending);
  return { results };
};

const builder = new StateGraph(State)
  .addNode("callApi", callApi)
  .addEdge(START, "callApi")
  .addEdge("callApi", END);

const checkpointer = new MemorySaver();
const graph = builder.compile({ checkpointer });

const threadId = uuid7();
const config = { configurable: { thread_id: threadId } };

// :remove-start:
const originalFetch = globalThis.fetch;
globalThis.fetch = async (url) => {
  if (url !== "https://www.example.com") {
    throw new Error(`Unexpected URL: ${url}`);
  }
  return new Response("Example response body");
};
// :remove-end:
await graph.invoke({ urls: ["https://www.example.com"] }, config);
// :remove-start:
const state = await graph.getState(config);
if (JSON.stringify(state.values.results) !== JSON.stringify(["Example response body"])) {
  throw new Error(`Unexpected results: ${JSON.stringify(state.values.results)}`);
}
globalThis.fetch = originalFetch;
console.log("✓ graph API task sample works correctly");
// :remove-end:
// :snippet-end:
