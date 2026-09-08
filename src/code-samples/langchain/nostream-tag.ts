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

const contentToText = (content: unknown): string => {
  if (typeof content === "string") {
    return content;
  }
  if (Array.isArray(content)) {
    return content
      .map((block) => {
        if (
          typeof block === "object" &&
          block !== null &&
          "text" in block &&
          typeof (block as { text?: unknown }).text === "string"
        ) {
          return (block as { text: string }).text;
        }
        return "";
      })
      .filter(Boolean)
      .join("\n");
  }
  return "";
};

const writeAnswer = async (state: typeof State.State) => {
  const r = await streamModel.invoke([
    { role: "user", content: `Reply briefly about ${state.topic}` },
  ]);
  return { answer: contentToText(r.content) };
};

const internalNotes = async (state: typeof State.State) => {
  // Tokens from this model are omitted from streamMode: "messages" because of nostream
  const r = await internalModel.invoke([
    { role: "user", content: `Private notes on ${state.topic}` },
  ]);
  return { notes: contentToText(r.content) };
};

const graph = new StateGraph(State)
  .addNode("writeAnswer", writeAnswer)
  .addNode("internal_notes", internalNotes)
  .addEdge(START, "writeAnswer")
  .addEdge("writeAnswer", "internal_notes")
  .compile();

const stream = await graph.streamEvents(
  { topic: "AI", answer: "", notes: "" },
  { version: "v3" },
);
// :snippet-end:

// :remove-start:
const streamedNodes: string[] = [];
for await (const message of stream.messages) {
  if (message.node) {
    streamedNodes.push(message.node);
  }
}

if (streamedNodes.includes("internal_notes")) {
  throw new Error(
    "No tokens from the nostream model should appear in the stream",
  );
}

console.log("\n✓ nostream tag example works as expected");
// :remove-end:
