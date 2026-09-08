// :snippet-start: customization-structured-output-js
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent } from "deepagents";
import { z } from "zod";

const internetSearch = tool(
  async ({
    query,
    maxResults = 5,
    topic = "general",
    includeRawContent = false,
  }: {
    query: string;
    maxResults?: number;
    topic?: "general" | "news" | "finance";
    includeRawContent?: boolean;
  }) => {
    const tavilySearch = new TavilySearch({
      maxResults,
      tavilyApiKey: process.env.TAVILY_API_KEY,
      includeRawContent,
      topic,
    });
    return await tavilySearch._call({ query });
  },
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({
      query: z.string().describe("The search query"),
      maxResults: z.number().optional().default(5),
      topic: z
        .enum(["general", "news", "finance"])
        .optional()
        .default("general"),
      includeRawContent: z.boolean().optional().default(false),
    }),
  },
);

const weatherReportSchema = z.object({
  location: z.string().describe("The location for this weather report"),
  temperature: z.number().describe("Current temperature in Celsius"),
  condition: z
    .string()
    .describe("Current weather condition (e.g., sunny, cloudy, rainy)"),
  humidity: z.number().describe("Humidity percentage"),
  windSpeed: z.number().describe("Wind speed in km/h"),
  forecast: z.string().describe("Brief forecast for the next 24 hours"),
});

const agent = await createDeepAgent({
  responseFormat: weatherReportSchema,
  tools: [internetSearch],
});

const result = await agent.invoke({
  messages: [
    {
      role: "user",
      content: "What's the weather like in San Francisco?",
    },
  ],
});

console.log(result.structuredResponse);
// {
//   location: 'San Francisco, California',
//   temperature: 18.3,
//   condition: 'Sunny',
//   humidity: 48,
//   windSpeed: 7.6,
//   forecast: 'Clear skies with temperatures remaining mild. High of 18°C (64°F) during the day, dropping to around 11°C (52°F) at night.'
// }
// :snippet-end:

// :remove-start:
if (!result) throw new Error("No result returned");
// :remove-end:
