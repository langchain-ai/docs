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

for await (const chunk of await agent.stream(
  { messages: [{ role: "user", content: "what is the weather in sf" }] },
  { ...config, streamMode: "updates", version: "v2" },
)) {
  const [step, content] = Object.entries(chunk)[0];
  console.log(`step: ${step}`);
  console.log(`content: ${JSON.stringify(content, null, 2)}`);
}
/**
 * step: model_request
 * content: {
 *   "messages": [
 *     {
 *       "kwargs": {
 *         // ...
 *         "tool_calls": [
 *           {
 *             "name": "get_weather",
 *             "args": {
 *               "city": "San Francisco"
 *             },
 *             "type": "tool_call",
 *             "id": "call_0qLS2Jp3MCmaKJ5MAYtr4jJd"
 *           }
 *         ],
 *         // ...
 *       }
 *     }
 *   ]
 * }
 * step: tools
 * content: {
 *   "messages": [
 *     {
 *       "kwargs": {
 *         "content": "The weather in San Francisco is always sunny!",
 *         "name": "get_weather",
 *         // ...
 *       }
 *     }
 *   ]
 * }
 * step: model_request
 * content: {
 *   "messages": [
 *     {
 *       "kwargs": {
 *         "content": "The latest update says: The weather in San Francisco is always sunny!\n\nIf you'd like real-time details (current temperature, humidity, wind, and today's forecast), I can pull the latest data for you. Want me to fetch that?",
 *         // ...
 *       }
 *     }
 *   ]
 * }
 */
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
