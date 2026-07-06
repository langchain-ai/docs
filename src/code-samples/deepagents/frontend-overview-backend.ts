// :remove-start:
console.log("✓ frontend-overview-backend sample validated");
process.exit(0);
// :remove-end:

// :snippet-start: frontend-overview-backend-js
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  tools: [getWeather],
  systemPrompt: "You are a helpful assistant",
  subagents: [
    {
      name: "researcher",
      description: "Research assistant",
      systemPrompt: "You are a research assistant.",
    },
  ],
});
// :snippet-end:
