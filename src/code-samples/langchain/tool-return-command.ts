// :snippet-start: tool-return-command-js
import { tool, ToolMessage, type ToolRuntime } from "langchain";
import { Command } from "@langchain/langgraph";
import * as z from "zod";

const setLanguage = tool(
  async ({ language }, config: ToolRuntime) => {
    return new Command({
      update: {
        preferredLanguage: language,
        messages: [
          new ToolMessage({
            content: `Language set to ${language}.`,
            tool_call_id: config.toolCallId,
          }),
        ],
      },
    });
  },
  {
    name: "set_language",
    description: "Set the preferred response language.",
    schema: z.object({ language: z.string() }),
  },
);
// :snippet-end:

// :remove-start:
async function main() {
  const mockConfig = {
    toolCallId: "test_call_123",
  } as ToolRuntime;

  const result = await setLanguage.invoke({ language: "Spanish" }, mockConfig);

  if (
    !(result instanceof Command) ||
    result.update.preferredLanguage !== "Spanish" ||
    result.update.messages.length !== 1 ||
    result.update.messages[0].content !== "Language set to Spanish." ||
    result.update.messages[0].tool_call_id !== "test_call_123"
  ) {
    throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
  }

  console.log("✓ Tool works as expected");
}
main();
// :remove-end:
