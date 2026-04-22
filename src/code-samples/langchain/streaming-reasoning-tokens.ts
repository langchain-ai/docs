// :snippet-start: streaming-reasoning-tokens-js
import z from "zod";
import { createAgent, tool } from "langchain";
import { ChatAnthropic } from "@langchain/anthropic";

const getWeather = tool(
  async ({ city }) => {
    return `It's always sunny in ${city}!`;
  },
  {
    name: "get_weather",
    description: "Get weather for a given city.",
    schema: z.object({ city: z.string() }),
  },
);

const agent = createAgent({
  model: new ChatAnthropic({
    // KEEP MODEL
    model: "claude-sonnet-4-6",
    thinking: { type: "enabled", budget_tokens: 5000 },
  }),
  tools: [getWeather],
});

for await (const [token, metadata] of await agent.stream(
  { messages: [{ role: "user", content: "What is the weather in SF?" }] },
  { streamMode: "messages" }, // [!code highlight]
)) {
  if (!token.contentBlocks) continue;
  const reasoning = token.contentBlocks.filter((b) => b.type === "reasoning");
  const text = token.contentBlocks.filter((b) => b.type === "text");
  if (reasoning.length) {
    process.stdout.write(`[thinking] ${reasoning[0].reasoning}`);
  }
  if (text.length) {
    process.stdout.write(text[0].text);
  }
}
// :snippet-end:

// :remove-start:
// This test is disabled because it requires an API key and would make actual API calls
// To run manually:
//   export ANTHROPIC_API_KEY=your_key
//   npx tsx src/code-samples/langchain/streaming-reasoning-tokens.ts
console.log("\n✓ Code sample is syntactically valid");
// :remove-end:
