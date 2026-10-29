// :remove-start:
// Setup that the docs snippet leaves out: state and a builder with the nodes
// the snippet refers to.
import {
  END,
  ReducedValue,
  START,
  StateGraph,
  StateSchema,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  subjects: z.array(z.string()).default(() => []),
  foo: z.string().optional(),
  jokes: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (left, right) => left.concat(right) }
  ),
});

const graph = new StateGraph(State)
  .addNode("nodeA", () => ({}))
  .addNode("generateJoke", (state: { subject?: string }) => ({
    jokes: [`Joke about ${state.subject}`],
  }));
// :remove-end:

// :snippet-start: langgraph-use-graph-api-send-command-js
import { Command, Send } from "@langchain/langgraph";

// Send: fan out one worker per item
graph.addConditionalEdges("nodeA", (state) => {
  return state.subjects.map(
    (subject) => new Send("generateJoke", { subject })
  );
});

// Command: update state and route in one return
graph.addNode(
  "myNode",
  (state) => {
    return new Command({
      update: { foo: "bar" },
      goto: "myOtherNode",
    });
  },
  { ends: ["myOtherNode"] }
);
// :snippet-end:

// :remove-start:
graph.addNode("myOtherNode", (state: { foo?: string }) => ({
  foo: `${state.foo}!`,
}));
graph.addEdge(START, "nodeA");
graph.addEdge("generateJoke", "myNode");
graph.addEdge("myOtherNode", END);
const compiled = graph.compile();
const sendResult = await compiled.invoke({ subjects: ["cats", "dogs"] });
if (
  JSON.stringify([...sendResult.jokes].sort()) !==
  JSON.stringify(["Joke about cats", "Joke about dogs"])
) {
  throw new Error(`unexpected jokes: ${JSON.stringify(sendResult.jokes)}`);
}
if (sendResult.foo !== "bar!") {
  throw new Error(`expected foo "bar!", got ${sendResult.foo}`);
}
console.log("✓ langgraph-use-graph-api-send-command-js validated");
// :remove-end:
