// :remove-start:
// Constructing chat models needs a credential even though no request is sent.
process.env.ANTHROPIC_API_KEY ??= "test-key";
process.env.OPENAI_API_KEY ??= "test-key";
// :remove-end:

// :snippet-start: langgraph-graph-api-nodes-runtime-llm-js
import { ChatOpenAI } from "@langchain/openai";
import { ChatAnthropic } from "@langchain/anthropic";
import { StateGraph, StateSchema, MessagesValue, GraphNode, START, END } from "@langchain/langgraph";
import * as z from "zod";

const ContextSchema = z.object({
  modelProvider: z.string().default("anthropic"),
});

const State = new StateSchema({
  messages: MessagesValue,
});

const MODELS = {
  anthropic: new ChatAnthropic({ model: "claude-haiku-4-5-20251001" }),
  openai: new ChatOpenAI({ model: "gpt-5.4-mini" }),
};

const callModel: GraphNode<typeof State> = async (state, config) => {
  const modelProvider = config?.context?.modelProvider || "anthropic";
  const model = MODELS[modelProvider as keyof typeof MODELS];
  const response = await model.invoke(state.messages);
  return { messages: [response] };
};

const graph = new StateGraph(State, ContextSchema)
  .addNode("model", callModel)
  .addEdge(START, "model")
  .addEdge("model", END)
  .compile();
// :remove-start:
// Construction only: stop before the invocations below, which call live models.
if (!("model" in graph.nodes)) throw new Error("model node missing");
if (!MODELS.anthropic || !MODELS.openai) throw new Error("models not created");
console.log("✓ langgraph-graph-api-nodes-runtime-llm-js validated (construction only)");
process.exit(0);
// :remove-end:

// Usage
const inputMessage = { role: "user", content: "hi" };
// With no configuration, uses default (Anthropic)
const response1 = await graph.invoke({ messages: [inputMessage] });
// Or, can set OpenAI
const response2 = await graph.invoke(
  { messages: [inputMessage] },
  { context: { modelProvider: "openai" } },
);

console.log(response1.messages.at(-1)?.response_metadata?.model);
console.log(response2.messages.at(-1)?.response_metadata?.model);
// :snippet-end:
