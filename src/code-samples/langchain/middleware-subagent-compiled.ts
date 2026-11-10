// :remove-start:
process.env.OPENAI_API_KEY ??= "sk-test-key";
process.env.ANTHROPIC_API_KEY ??= "sk-ant-test-key";
// :remove-end:

// :snippet-start: middleware-subagent-compiled-js
import { tool, createAgent } from "langchain";
import { createSubAgentMiddleware, type SubAgent } from "deepagents";
import { z } from "zod";

const getWeather = tool(
  async ({ city }: { city: string }) => {
    return `The weather in ${city} is sunny.`;
  },
  {
    name: "get_weather",
    description: "Get the weather in a city.",
    schema: z.object({
      city: z.string(),
    }),
  },
);

const weatherSubagent: SubAgent = {
  name: "weather",
  description: "This subagent can get weather in cities.",
  systemPrompt: "Use the get_weather tool to get the weather in a city.",
  tools: [getWeather],
  model: "gpt-6.1",
  middleware: [],
};

const agent = createAgent({
  model: "claude-sonnet-4-6",
  middleware: [
    createSubAgentMiddleware({
      defaultModel: "claude-sonnet-4-6",
      defaultTools: [],
      subagents: [weatherSubagent],
    }),
  ],
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ middleware-subagent-compiled validated");
// :remove-end:
