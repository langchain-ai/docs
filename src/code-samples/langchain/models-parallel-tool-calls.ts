// :remove-start:
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "langchain";
import { z } from "zod";

const getWeather = tool(
  async ({ city }: { city: string }) => `Weather in ${city} is sunny`,
  {
    name: "get_weather",
    description: "Get the weather for a city",
    schema: z.object({ city: z.string() }),
  },
);

const messages = [
  {
    role: "user" as const,
    content: "What is the weather in Boston?",
  },
];

const hasLiveKey =
  Boolean(process.env.OPENAI_API_KEY) &&
  !process.env.OPENAI_API_KEY.startsWith("sk-test");

const model = hasLiveKey
  ? new ChatOpenAI({ model: "gpt-5.4-mini" })
  : {
      bindTools: (_tools: unknown) => ({
        invoke: async (
          _messages: unknown,
          _options?: { parallel_tool_calls?: boolean },
        ) => ({ content: "ok" }),
      }),
    };
// :remove-end:

// :snippet-start: models-parallel-tool-calls-js
await model.bindTools([getWeather]).invoke(messages, {
  parallel_tool_calls: false,
});
// :snippet-end:

// :remove-start:
console.log("✓ models-parallel-tool-calls validated");
// :remove-end:
