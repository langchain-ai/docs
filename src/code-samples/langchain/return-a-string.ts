// :snippet-start: tool-return-values
import { tool } from "langchain";
import * as z from "zod";

const getWeather = tool(({ city }) => `It is currently sunny in ${city}.`, {
  name: "get_weather",
  description: "Get weather for a city.",
  schema: z.object({ city: z.string() }),
});
// :snippet-end:

// :remove-start:
async function main() {
  const result = await getWeather.invoke({ city: "San Francisco" });
  if (result !== "It is currently sunny in San Francisco.") {
    throw new Error(
      `Expected "It is currently sunny in San Francisco.", got "${result}"`,
    );
  }
  console.log("✓ Tool works as expected");
}
main();
// :remove-end:
