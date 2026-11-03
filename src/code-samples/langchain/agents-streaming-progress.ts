import { createAgent, tool } from "langchain";
import * as z from "zod";

// :remove-start:
const search = tool(({ query }) => `Results for: ${query}`, {
  name: "search",
  description: "Search for information",
  schema: z.object({ query: z.string() }),
});

const agent = createAgent({
  model: "openai:gpt-5.4",
  tools: [search],
});
// :remove-end:
// :snippet-start: agents-streaming-progress-js
const stream = await agent.streamEvents(
  {
    messages: [
      {
        role: "user",
        content: "Search for AI news and summarize the findings",
      },
    ],
  },
  { version: "v3" },
);

for await (const snapshot of stream.values) {
  // Each snapshot contains the full state at that point
  const latestMessage = snapshot.messages.at(-1);
  if (latestMessage?.content) {
    if (latestMessage.type === "human") {
      console.log(`User: ${latestMessage.content}`);
    } else if (latestMessage.type === "ai") {
      console.log(`Agent: ${latestMessage.content}`);
    }
  } else if (latestMessage?.tool_calls?.length) {
    const toolCallNames = latestMessage.tool_calls.map((tc) => tc.name);
    console.log(`Calling tools: ${toolCallNames.join(", ")}`);
  }
}
// :snippet-end:

// :remove-start:
async function main() {
  const collected: unknown[] = [];
  const testStream = await agent.streamEvents(
    {
      messages: [
        {
          role: "user",
          content: "Search for AI news and summarize the findings",
        },
      ],
    },
    { version: "v3" },
  );
  await Promise.all([
    (async () => {
      for await (const snapshot of testStream.values) {
        collected.push(snapshot);
      }
    })(),
    testStream.output,
  ]);
  if (collected.length === 0) {
    throw new Error("expected at least one stream values snapshot");
  }
  console.log(
    "✓ agents streaming progress (streamEvents v3) emits value snapshots",
  );
}

main();
// :remove-end:
