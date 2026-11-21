// :snippet-start: langgraph-fault-tolerance-llm-recoverable-js
import { Command, GraphNode, StateSchema } from "@langchain/langgraph";
import * as z from "zod";

class ToolError extends Error {}

const State = new StateSchema({
  toolCall: z.string(),
  toolResult: z.string().optional(),
});

async function runTool(toolCall: string): Promise<string> {
  if (toolCall === "bad") {
    throw new ToolError("invalid args");
  }
  return `ok:${toolCall}`;
}

const executeTool: GraphNode<typeof State> = async (state) => {
  try {
    const result = await runTool(state.toolCall);
    return new Command({
      update: { toolResult: result },
      goto: "agent",
    });
  } catch (error) {
    // Let the LLM see what went wrong and try again
    return new Command({
      update: { toolResult: `Tool error: ${error}` },
      goto: "agent",
    });
  }
};
// :snippet-end:

// :remove-start:
function asCommand(value: unknown): Command {
  if (!(value instanceof Command)) {
    throw new Error(`Expected Command, got ${JSON.stringify(value)}`);
  }
  return value;
}

function gotoIncludes(cmd: Command, dest: string): boolean {
  const goto = cmd.goto;
  return Array.isArray(goto) ? goto.includes(dest) : goto === dest;
}

const failed = asCommand(
  await executeTool({ toolCall: "bad" }, {} as never),
);
if (!gotoIncludes(failed, "agent")) {
  throw new Error(`Expected goto agent, got ${JSON.stringify(failed)}`);
}
if (failed.update?.toolResult !== "Tool error: Error: invalid args") {
  throw new Error(`Unexpected toolResult: ${failed.update?.toolResult}`);
}

const ok = asCommand(
  await executeTool({ toolCall: "search" }, {} as never),
);
if (!gotoIncludes(ok, "agent") || ok.update?.toolResult !== "ok:search") {
  throw new Error(`Unexpected ok result: ${JSON.stringify(ok)}`);
}
console.log("✓ langgraph-fault-tolerance-llm-recoverable-js validated");
// :remove-end:
