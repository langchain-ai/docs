// :remove-start:
process.env.OPENAI_API_KEY ??= "sk-test-key";
process.env.ANTHROPIC_API_KEY ??= "sk-ant-test-key";
// :remove-end:

// :snippet-start: middleware-subagent-js
import { tool } from "langchain";
import { createAgent } from "langchain";
import { createSubAgentMiddleware } from "deepagents";
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

const agent = createAgent({
  model: "claude-sonnet-4-6",
  middleware: [
    createSubAgentMiddleware({
      defaultModel: "claude-sonnet-4-6",
      defaultTools: [],
      subagents: [
        {
          name: "weather",
          description: "This subagent can get weather in cities.",
          systemPrompt: "Use the get_weather tool to get the weather in a city.",
          tools: [getWeather],
          model: "gpt-6.1-sol",
          middleware: [],
        },
      ],
    }),
  ],
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
console.log("✓ middleware-subagent validated");
// :remove-end:
