// :remove-start:
function strictVerification(claim: string): string {
  return `strict verified: ${claim}`;
}
function basicVerification(claim: string): string {
  return `basic verified: ${claim}`;
}
// :remove-end:

// :snippet-start: subagents-per-subagent-context-js
import { tool } from "langchain";
import type { ToolRuntime } from "@langchain/core/tools";
import { z } from "zod";

const contextSchema = z.object({
  userId: z.string(),
  researcherMaxDepth: z.number().optional(),
  factCheckerStrictMode: z.boolean().optional(),
});

const verifyClaim = tool(
  async (input, runtime: ToolRuntime<unknown, typeof contextSchema>) => {
    const strictMode = runtime.context?.factCheckerStrictMode ?? false;
    if (strictMode) {
      return strictVerification(input.claim);
    }
    return basicVerification(input.claim);
  },
  {
    name: "verify_claim",
    description: "Verify a factual claim",
    schema: z.object({ claim: z.string() }),
  },
);
// :snippet-end:

// :remove-start:
import { createDeepAgent } from "deepagents";

const verifyResult = await verifyClaim.invoke(
  { claim: "test claim" },
  { context: { userId: "user-123", factCheckerStrictMode: true } },
);
if (!verifyResult.includes("strict verified")) {
  throw new Error(`unexpected verify output: ${verifyResult}`);
}

const perSubagentAgent = createDeepAgent({
  model: "google_genai:gemini-3.5-flash",
  subagents: [
    {
      name: "fact-checker",
      description: "Verifies factual claims",
      systemPrompt: "You verify claims carefully.",
      tools: [verifyClaim],
    },
  ],
  contextSchema,
});
if (!perSubagentAgent) throw new Error("agent not created");
console.log("✓ subagents-per-subagent-context validated");
// :remove-end:
