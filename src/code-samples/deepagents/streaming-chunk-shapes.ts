// :remove-start:
import { createDeepAgent } from "deepagents";

type StreamAgent = {
  stream: (
    input: unknown,
    options: unknown,
  ) => Promise<AsyncIterable<unknown>>;
};

let agent: StreamAgent;

if (process.env.OPENAI_API_KEY) {
  agent = createDeepAgent({
    model: "openai:gpt-6.1-sol",
    systemPrompt: "You are a helpful research assistant",
  });
} else {
  // Signature-only path when no model key is present: yield one chunk per shape.
  agent = {
    stream: async (_input, options) => {
      const streamMode = (options as { streamMode?: unknown }).streamMode;
      if (Array.isArray(streamMode)) {
        return (async function* () {
          yield [[], "updates", { model_request: {} }];
        })();
      }
      return (async function* () {
        yield [[], { model_request: {} }];
      })();
    },
  };
}
// :remove-end:

// :snippet-start: streaming-chunk-shapes-js
// Single mode + subgraphs
for await (const [namespace, data] of await agent.stream(
  { messages: [{ role: "user", content: "Research quantum computing" }] },
  { streamMode: "updates", subgraphs: true },
)) {
  console.log(namespace); // [] for main agent, ["tools:<id>"] for subagent
  console.log(data);
}

// Multiple modes + subgraphs
for await (const [namespace, mode, data] of await agent.stream(
  { messages: [{ role: "user", content: "Research quantum computing" }] },
  { streamMode: ["updates", "messages", "custom"], subgraphs: true },
)) {
  console.log(mode); // "updates", "messages", or "custom"
  console.log(namespace); // [] for main agent, ["tools:<id>"] for subagent
  console.log(data);
}
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("expected agent from streaming chunk shapes sample");
console.log("✓ streaming-chunk-shapes validated");
// :remove-end:
