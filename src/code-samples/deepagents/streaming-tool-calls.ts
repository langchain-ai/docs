// :remove-start:
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  systemPrompt:
    "You are a project coordinator with no research knowledge. " +
    "For every user request, you must call the task() tool with " +
    "subagent_type set to researcher. Never answer research questions yourself. " +
    "Keep your final response to one sentence.",
  subagents: [
    {
      name: "researcher",
      description: "Researches topics thoroughly",
      systemPrompt:
        "You are a thorough researcher. Research the given topic " +
        "and provide a concise summary in 2-3 sentences.",
    },
  ],
});
// :remove-end:

// :snippet-start: streaming-tool-calls-js
import { AIMessageChunk, ToolMessage } from "langchain";

for await (const [namespace, chunk] of await agent.stream(
  {
    messages: [
      {
        role: "user",
        content: "Research recent quantum computing advances",
      },
    ],
  },
  { streamMode: "messages", subgraphs: true },
)) {
  const [message] = chunk;

  // Identify source: "main" or the subagent namespace segment
  const isSubagent = namespace.some((s: string) => s.startsWith("tools:"));
  const source = isSubagent
    ? namespace.find((s: string) => s.startsWith("tools:"))!
    : "main";

  // Tool call chunks (streaming tool invocations)
  if (AIMessageChunk.isInstance(message) && message.tool_call_chunks?.length) {
    for (const tc of message.tool_call_chunks) {
      if (tc.name) {
        console.log(`\n[${source}] Tool call: ${tc.name}`);
      }
      // Args stream in chunks - write them incrementally
      if (tc.args) {
        process.stdout.write(tc.args);
      }
    }
  }

  // Tool results
  if (ToolMessage.isInstance(message)) {
    console.log(
      `\n[${source}] Tool result [${message.name}]: ${message.text?.slice(0, 150)}`,
    );
  }

  // Regular AI content (skip tool call messages)
  if (
    AIMessageChunk.isInstance(message) &&
    message.text &&
    !message.tool_call_chunks?.length
  ) {
    process.stdout.write(message.text);
  }
}

process.stdout.write("\n");
// :snippet-end:

// :remove-start:
console.log("✓ streaming-tool-calls validated");
// :remove-end:
