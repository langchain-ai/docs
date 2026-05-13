// :snippet-start: graph-api-using-tasks-original-js
import { v7 as uuid7 } from "uuid";
import * as z from "zod";

import {
  END,
  MemorySaver,
  START,
  StateGraph,
  StateSchema,
} from "@langchain/langgraph";
import type { GraphNode } from "@langchain/langgraph";

const State = new StateSchema({
  url: z.string(),
  result: z.string().optional(),
});

const callApi: GraphNode<typeof State> = async (state) => {
  const response = await fetch(state.url);  // [!code highlight]
  const text = await response.text();
  const result = text.slice(0, 100);
  return { result };
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
await graph.invoke({ url: "https://www.example.com" }, config);
// :remove-start:
const state = await graph.getState(config);
if (state.values.result !== "Example response body") {
  throw new Error(`Unexpected result: ${state.values.result}`);
}
globalThis.fetch = originalFetch;
console.log("✓ graph API original sample works correctly");
// :remove-end:
// :snippet-end:
