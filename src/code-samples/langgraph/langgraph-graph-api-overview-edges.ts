// :remove-start:
import { StateGraph, StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({ text: z.string() });

// The snippets below add one edge form each, so build a fresh graph per snippet.
// Plain strings stand in for START and END, which the snippets import themselves.
const buildGraph = (...names: string[]) => {
  let builder: any = new StateGraph(State);
  for (const name of names) {
    const suffix = name.slice(-1).toLowerCase();
    builder = builder.addNode(name, (state: { text: string }) => ({
      text: `${state.text}${suffix}`,
    }));
  }
  return builder;
};

const START_NODE = "__start__";
const END_NODE = "__end__";

async function expectText(compiled: { invoke: (input: { text: string }) => Promise<{ text: string }> }, expected: string, name: string) {
  const result = await compiled.invoke({ text: "" });
  if (result.text !== expected) {
    throw new Error(`${name}: expected "${expected}", got "${result.text}"`);
  }
  console.log(`✓ ${name}`);
}

let graph: any = buildGraph("nodeA");
graph.addEdge("nodeA", END_NODE);
// :remove-end:
// :snippet-start: langgraph-graph-api-overview-start-js
import { START } from "@langchain/langgraph";

graph.addEdge(START, "nodeA");
// :snippet-end:

// :remove-start:
await expectText(graph.compile(), "a", "langgraph-graph-api-overview-start-js");

graph = buildGraph("nodeA");
graph.addEdge(START_NODE, "nodeA");
// :remove-end:
// :snippet-start: langgraph-graph-api-overview-end-js
import { END } from "@langchain/langgraph";

graph.addEdge("nodeA", END);
// :snippet-end:

// :remove-start:
await expectText(graph.compile(), "a", "langgraph-graph-api-overview-end-js");

graph = buildGraph("nodeA", "nodeB");
graph.addEdge(START_NODE, "nodeA");
graph.addEdge("nodeB", END_NODE);
// :remove-end:
// :snippet-start: langgraph-graph-api-overview-normal-edge-js
graph.addEdge("nodeA", "nodeB");
// :snippet-end:

// :remove-start:
await expectText(graph.compile(), "ab", "langgraph-graph-api-overview-normal-edge-js");

let routingFunction = (_state: unknown) => "pathA";

// A node can register a routing function once, so test each form on a fresh graph.
const withoutMap = buildGraph("nodeA", "nodeB", "nodeC");
withoutMap.addEdge(START_NODE, "nodeA");
withoutMap.addEdge("nodeB", END_NODE);
withoutMap.addEdge("nodeC", END_NODE);
withoutMap.addConditionalEdges("nodeA", routingFunction);
withoutMap.compile();

graph = buildGraph("nodeA", "nodeB", "nodeC");
graph.addEdge(START_NODE, "nodeA");
graph.addEdge("nodeB", END_NODE);
graph.addEdge("nodeC", END_NODE);
// :remove-end:
// :snippet-start: langgraph-graph-api-overview-conditional-edges-js
graph.addConditionalEdges("nodeA", routingFunction);
// Or with an explicit map:
// :remove-start:
graph = buildGraph("nodeA", "nodeB", "nodeC");
graph.addEdge(START_NODE, "nodeA");
graph.addEdge("nodeB", END_NODE);
graph.addEdge("nodeC", END_NODE);
// :remove-end:
graph.addConditionalEdges("nodeA", routingFunction, {
  pathA: "nodeB",
  pathB: "nodeC",
});
// :snippet-end:

// :remove-start:
await expectText(graph.compile(), "ab", "langgraph-graph-api-overview-conditional-edges-js");

graph = buildGraph("nodeA");
graph.addEdge("nodeA", END_NODE);
// :remove-end:
// :snippet-start: langgraph-graph-api-overview-entry-point-js
graph.addEdge(START, "nodeA");
// :snippet-end:

// :remove-start:
await expectText(graph.compile(), "a", "langgraph-graph-api-overview-entry-point-js");

routingFunction = (_state: unknown) => "true";

graph = buildGraph("nodeB", "nodeC");
graph.addEdge("nodeB", END_NODE);
graph.addEdge("nodeC", END_NODE);
// :remove-end:
// :snippet-start: langgraph-graph-api-overview-conditional-entry-point-js
graph.addConditionalEdges(START, routingFunction, {
  true: "nodeB",
  false: "nodeC",
});
// :snippet-end:

// :remove-start:
await expectText(graph.compile(), "b", "langgraph-graph-api-overview-conditional-entry-point-js");
// :remove-end:
