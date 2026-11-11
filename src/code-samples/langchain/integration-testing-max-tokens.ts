// Integration testing: cap max tokens on the chat model.

// :remove-start:
process.env.GOOGLE_API_KEY ??= "test-key";
process.env.GEMINI_API_KEY ??= "test-key";

import { tool } from "langchain";
import * as z from "zod";

const getWeather = tool(
  ({ city }: { city: string }) => `It is sunny in ${city}.`,
  {
    name: "get_weather",
    description: "Get weather for a city.",
    schema: z.object({ city: z.string() }),
  },
);
// :remove-end:

// :snippet-start: integration-testing-max-tokens-js
import { createAgent, initChatModel } from "langchain";

const model = await initChatModel("google-genai:gemini-3.1-flash-lite", {
  maxOutputTokens: 256,
});

const agent = createAgent({
  model,
  tools: [getWeather],
});
// :snippet-end:

// :remove-start:
const defaultConfig = (
  model as { _defaultConfig?: { maxOutputTokens?: number } }
)._defaultConfig;
if (defaultConfig?.maxOutputTokens !== 256) {
  throw new Error(
    `expected maxOutputTokens 256, got ${defaultConfig?.maxOutputTokens}`,
  );
}
if (!agent) {
  throw new Error("expected agent");
}
console.log("✓ integration-testing-max-tokens validated");
// :remove-end:
