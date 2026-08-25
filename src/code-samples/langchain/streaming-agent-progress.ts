// :snippet-start: streaming-agent-progress-js
import { createAgent, tool } from "langchain";
import { MemorySaver } from "@langchain/langgraph";
import z from "zod";

const getWeather = tool(
  async ({ city }) => {
    return `The weather in ${city} is always sunny!`;
  },
  {
    name: "get_weather",
    description: "Get weather for a given city.",
    schema: z.object({
      city: z.string(),
    }),
  },
);

const agent = createAgent({
  model: "gpt-5-nano",
  tools: [getWeather],
  checkpointer: new MemorySaver(),
});

const config = { configurable: { thread_id: crypto.randomUUID() } };

const stream = await agent.streamEvents(
  { messages: [{ role: "user", content: "what is the weather in sf" }] },
  { ...config, version: "v3" },
);
await Promise.all([
  (async () => {
    for await (const message of stream.messages) {
      for await (const token of message.text) {
        process.stdout.write(token);
      }
    }
  })(),
  (async () => {
    for await (const call of stream.toolCalls) {
      console.log(`\nTool call: ${call.name}(${JSON.stringify(call.input)})`);
      console.log(`Tool result: ${await call.output}`);
    }
  })(),
]);

const finalState = await stream.output;
// Tool call: get_weather({"city":"San Francisco"})
// Tool result: [object ToolMessage]
// According to the data I have, the weather in San Francisco is always sunny! Would you like current conditions or a short forecast for today or the next few days?
// :snippet-end:

// :remove-start:
async function main() {
  let messagesSeen = 0;
  const stream = await agent.streamEvents(
    { messages: [{ role: "user", content: "what is the weather in sf" }] },
    {
      configurable: { thread_id: crypto.randomUUID() },
      version: "v3",
    },
  );
  await Promise.all([
    (async () => {
      for await (const message of stream.messages) {
        messagesSeen += 1;
        for await (const _ of message.text) {
          // Drain text deltas.
        }
      }
    })(),
    (async () => {
      for await (const call of stream.toolCalls) {
        await call.output;
      }
    })(),
    stream.output,
  ]);
  if (messagesSeen === 0) {
    throw new Error("expected at least one streamed message");
  }
  console.log("✓ streaming agent progress (streamEvents v3) uses typed projections");
}

main();
// :remove-end:
