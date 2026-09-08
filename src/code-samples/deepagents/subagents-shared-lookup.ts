// :remove-start:
function strictLookup(query: string): string {
  return `strict: ${query}`;
}
function generalLookup(query: string): string {
  return `general: ${query}`;
}
// :remove-end:

// :snippet-start: subagents-shared-lookup-js
import { tool } from "langchain";
import type { ToolRuntime } from "@langchain/core/tools";
import { z } from "zod";

const sharedLookup = tool(
  async (input, runtime: ToolRuntime) => {
    const agentName = runtime.config?.metadata?.lc_agent_name;
    if (agentName === "fact-checker") {
      return strictLookup(input.query);
    }
    return generalLookup(input.query);
  },
  {
    name: "shared_lookup",
    description: "Look up information from various sources",
    schema: z.object({ query: z.string() }),
  },
);
// :snippet-end:

// :remove-start:
const lookupResult = await sharedLookup.invoke({ query: "test" });
if (!lookupResult.includes("general")) {
  throw new Error(`unexpected lookup output: ${lookupResult}`);
}
console.log("✓ subagents-shared-lookup validated");
// :remove-end:
