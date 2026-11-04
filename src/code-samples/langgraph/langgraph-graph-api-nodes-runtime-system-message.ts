// :remove-start:
// Constructing chat models needs a credential even though no request is sent.
process.env.ANTHROPIC_API_KEY ??= "test-key";
process.env.OPENAI_API_KEY ??= "test-key";
// :remove-end:

// :snippet-start: langgraph-graph-api-nodes-runtime-system-message-js
import { ChatOpenAI } from "@langchain/openai";
import { ChatAnthropic } from "@langchain/anthropic";
import { SystemMessage } from "@langchain/core/messages";
import { StateGraph, StateSchema, MessagesValue, GraphNode, START, END } from "@langchain/langgraph";
import * as z from "zod";

const ContextSchema = z.object({
  modelProvider: z.string().default("anthropic"),
  systemMessage: z.string().optional(),
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
  const systemMessage = config?.context?.systemMessage;

  const model = MODELS[modelProvider as keyof typeof MODELS];
  let messages = state.messages;

  if (systemMessage) {
    messages = [new SystemMessage(systemMessage), ...messages];
  }

  const response = await model.invoke(messages);
  return { messages: [response] };
};

const graph = new StateGraph(State, ContextSchema)
  .addNode("model", callModel)
  .addEdge(START, "model")
  .addEdge("model", END)
  .compile();
// :remove-start:
// Construction only: stop before the invocation below, which calls a live model.
if (!("model" in graph.nodes)) throw new Error("model node missing");
if (!MODELS.anthropic || !MODELS.openai) throw new Error("models not created");
console.log(
  "✓ langgraph-graph-api-nodes-runtime-system-message-js validated (construction only)",
);
process.exit(0);
// :remove-end:

// Usage
const inputMessage = { role: "user", content: "hi" };
const response = await graph.invoke(
  { messages: [inputMessage] },
  {
    context: {
      modelProvider: "openai",
      systemMessage: "Respond in Italian.",
    },
  }
);

for (const message of response.messages) {
  console.log(`${message.getType()}: ${message.content}`);
}
// :snippet-end:
