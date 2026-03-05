// :snippet-start: tool-return-object
import { tool } from "langchain";
import * as z from "zod";

const getWeatherData = tool(
  ({ city }) => ({
    city,
    temperature_c: 22,
    conditions: "sunny",
  }),
  {
    name: "get_weather_data",
    description: "Get structured weather data for a city.",
    schema: z.object({ city: z.string() }),
  }
);
// :snippet-end:

// :remove-start:
async function main() {
  const result = await getWeatherData.invoke({ city: "San Francisco" });
  if (
    result.city !== "San Francisco" ||
    result.temperature_c !== 22 ||
    result.conditions !== "sunny"
  ) {
    throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
  }
  console.log("✓ Tool works as expected");
}
main();
// :remove-end:
