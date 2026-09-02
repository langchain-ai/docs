// :remove-start:
function performSearch(
  query: string,
  options: { maxResults: number; includeRaw: boolean },
): string {
  return `search ${query} max=${options.maxResults} raw=${options.includeRaw}`;
}
// :remove-end:

// :snippet-start: subagents-flexible-search-js
import { tool } from "langchain";
import type { ToolRuntime } from "@langchain/core/tools";
import { z } from "zod";

const contextSchema = z.object({
  userId: z.string(),
  researcherMaxDepth: z.number().optional(),
  factCheckerStrictMode: z.boolean().optional(),
});

const flexibleSearch = tool(
  async (input, runtime: ToolRuntime<unknown, typeof contextSchema>) => {
    const agentName = runtime.config?.metadata?.lc_agent_name ?? "unknown";
    const ctx = runtime.context;
    const maxResults =
      agentName === "researcher" ? (ctx?.researcherMaxDepth ?? 5) : 5;
    const includeRaw = false;

    return performSearch(input.query, { maxResults, includeRaw });
  },
  {
    name: "flexible_search",
    description: "Search with agent-specific settings",
    schema: z.object({ query: z.string() }),
  },
);
// :snippet-end:

// :remove-start:
const searchResult = await flexibleSearch.invoke(
  { query: "quantum" },
  { context: { userId: "u1" } },
);
if (!searchResult.includes("max=5")) {
  throw new Error(`unexpected search output: ${searchResult}`);
}
console.log("✓ subagents-flexible-search validated");
// :remove-end:
