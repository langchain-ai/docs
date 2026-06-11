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
for await (const snapshot of stream.values) {
  console.log(
    `content: ${JSON.stringify(snapshot.messages.at(-1).contentBlocks, null, 2)}`,
  );
}
// :snippet-end:

// :remove-start:
async function main() {
  const collected: unknown[] = [];
  const stream = await agent.streamEvents(
    { messages: [{ role: "user", content: "what is the weather in sf" }] },
    {
      configurable: { thread_id: crypto.randomUUID() },
      version: "v3",
    },
  );
  await Promise.all([
    (async () => {
      for await (const snapshot of stream.values) {
        collected.push(snapshot);
      }
    })(),
    stream.output,
  ]);
  if (collected.length === 0) {
    throw new Error("expected at least one stream values snapshot");
  }
  console.log(
    "✓ streaming agent progress (streamEvents v3) emits value snapshots",
  );
}

main();
// :remove-end:
