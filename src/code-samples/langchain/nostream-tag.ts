/**
 * Example of using nostream tag to exclude LLM output from the stream.
 */

// :snippet-start: nostream-tag-js
import { ChatAnthropic } from "@langchain/anthropic";
import { StateGraph, StateSchema, START } from "@langchain/langgraph";
import * as z from "zod";

// KEEP MODEL
const streamModel = new ChatAnthropic({ model: "claude-haiku-4-5-20251001" });
const internalModel = new ChatAnthropic({
  // KEEP MODEL
  model: "claude-haiku-4-5-20251001",
}).withConfig({
  tags: ["nostream"],
});

const State = new StateSchema({
  topic: z.string(),
  answer: z.string().optional(),
  notes: z.string().optional(),
});

const writeAnswer = async (state: typeof State.State) => {
  const r = await streamModel.invoke([
    { role: "user", content: `Reply briefly about ${state.topic}` },
  ]);
  return { answer: r.content };
};

const internalNotes = async (state: typeof State.State) => {
  // Tokens from this model are omitted from streamMode: "messages" because of nostream
  const r = await internalModel.invoke([
    { role: "user", content: `Private notes on ${state.topic}` },
  ]);
  return { notes: r.content };
};

const graph = new StateGraph(State)
  .addNode("writeAnswer", writeAnswer)
  .addNode("internal_notes", internalNotes)
  .addEdge(START, "writeAnswer")
  .addEdge("writeAnswer", "internal_notes")
  .compile();

const stream = await graph.stream(
  { topic: "AI", answer: "", notes: "" },
  { streamMode: "messages" },
);
// :snippet-end:

// :remove-start:
const streamedNodes: string[] = [];
for await (const [msg, metadata] of stream) {
  if (msg.content) {
    streamedNodes.push(metadata.langgraph_node);
  }
}

if (streamedNodes.includes("internal_notes")) {
  throw new Error(
    "No tokens from the nostream model should appear in the stream",
  );
}

console.log("\n✓ nostream tag example works as expected");
// :remove-end:
