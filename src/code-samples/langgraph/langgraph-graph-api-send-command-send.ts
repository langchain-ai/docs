// :snippet-start: langgraph-graph-api-send-command-send-js
import {
  StateGraph,
  StateSchema,
  ReducedValue,
  GraphNode,
  ConditionalEdgeRouter,
  START,
  END,
  Send,
} from "@langchain/langgraph";
import * as z from "zod";

const OverallState = new StateSchema({
  topic: z.string(),
  subjects: z.array(z.string()),
  jokes: new ReducedValue(z.array(z.string()).default(() => []), {
    reducer: (x, y) => x.concat(y),
  }),
  bestSelectedJoke: z.string(),
});

const generateTopics: GraphNode<typeof OverallState> = (state) => {
  return { subjects: ["lions", "elephants", "penguins"] };
};

// Send passes { subject } as this invocation's input (not full OverallState)
const generateJoke = (state: { subject: string }) => {
  const jokeMap: Record<string, string> = {
    lions: "Why don't lions like fast food? Because they can't catch it!",
    elephants:
      "Why don't elephants use computers? They're afraid of the mouse!",
    penguins:
      "Why don't penguins like talking to strangers at parties? Because they find it hard to break the ice.",
  };
  return { jokes: [jokeMap[state.subject]] };
};

const continueToJokes: ConditionalEdgeRouter<{
  InputSchema: typeof OverallState;
  Nodes: "generateJoke";
}> = (state) => {
  return state.subjects.map(
    (subject) => new Send("generateJoke", { subject })
  );
};

const bestJoke: GraphNode<typeof OverallState> = (state) => {
  return { bestSelectedJoke: "penguins" };
};

const graph = new StateGraph(OverallState)
  .addNode("generateTopics", generateTopics)
  .addNode("generateJoke", generateJoke)
  .addNode("bestJoke", bestJoke)
  .addEdge(START, "generateTopics")
  .addConditionalEdges("generateTopics", continueToJokes)
  .addEdge("generateJoke", "bestJoke")
  .addEdge("bestJoke", END)
  .compile();
// :snippet-end:

// :snippet-start: langgraph-graph-api-send-command-send-stream-js
const stream = await graph.stream(
  { topic: "animals" },
  { streamMode: "updates" }
);
for await (const chunk of stream) {
  console.log(chunk);
}
// :snippet-end:

// :remove-start:
const result = await graph.invoke({ topic: "animals" });
if (result.jokes.length !== 3) {
  throw new Error(`Expected 3 jokes, got ${JSON.stringify(result.jokes)}`);
}
for (const subject of ["lions", "elephants", "penguins"]) {
  if (!result.jokes.some((joke: string) => joke.includes(subject))) {
    throw new Error(`Missing joke for ${subject}`);
  }
}
if (result.bestSelectedJoke !== "penguins") {
  throw new Error(`Unexpected best joke: ${result.bestSelectedJoke}`);
}
console.log("✓ langgraph-graph-api-send-command-send-js");
// :remove-end:
