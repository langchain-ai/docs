// Managed Deep Agents quickstart, Tavily variant: the custom search tool.
// Lives next to agent.ts so `import ... from "./tools/search"` resolves.

// :snippet-start: mda-quickstart-tavily-search-js
// :codegroup-tab: tools/search.ts
import { TavilySearch } from "@langchain/tavily";
import { tool } from "langchain";
import { connections } from "managed-deepagents";
import { z } from "zod";

export const internetSearch = tool(
  async ({ query, maxResults = 5, topic = "general" }) => {
    const tavilyApiKey = await connections.get("research-tavily", { type: "agent" });
    const tavilySearch = new TavilySearch({
      maxResults,
      tavilyApiKey,
      topic,
    });
    return tavilySearch._call({ query });
  },
  {
    name: "internet_search",
    description: "Search the internet for relevant sources.",
    schema: z.object({
      query: z.string().describe("The search query."),
      maxResults: z.number().optional().default(5),
      topic: z.enum(["general", "news", "finance"]).optional().default("general"),
    }),
  },
);
// :snippet-end:

// :remove-start:
if (internetSearch.name !== "internet_search") {
  throw new Error(`Expected internet_search, got ${internetSearch.name}`);
}
console.log("✓ internet_search tool defined with connections.get");
// :remove-end:
