// :snippet-start: streaming-agent-progress-js
import { v4 as uuidv4 } from "uuid";
import { createAgent } from "langchain";
import { MemorySaver } from "@langchain/langgraph";
import z from "zod";
import { createAgent, tool } from "langchain";

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

const config = { configurable: { thread_id: uuidv4() } };

for await (const chunk of await agent.stream(
  { messages: [{ role: "user", content: "what is the weather in sf" }] },
  { ...config, streamMode: "updates", version: "v2" },
)) {
  const [step, content] = Object.entries(chunk)[0];
  console.log(`step: ${step}`);
  console.log(`content: ${JSON.stringify(content, null, 2)}`);
}
/**
 * step: model
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
 * step: model
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
  for await (const chunk of await agent.stream(
    { messages: [{ role: "user", content: "what is the weather in sf" }] },
    {
      configurable: { thread_id: uuidv4() },
      streamMode: "updates",
      version: "v2",
    },
  )) {
    collected.push(chunk);
  }
  if (collected.length === 0) {
    throw new Error("expected at least one stream chunk");
  }
  console.log("✓ streaming agent progress (updates, v2) emits chunks");
}

main();
// :remove-end:
