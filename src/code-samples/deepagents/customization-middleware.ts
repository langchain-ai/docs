// :snippet-start: customization-middleware-js
import { tool, createMiddleware } from "langchain";
import { createDeepAgent } from "deepagents";
import * as z from "zod";

const getWeather = tool(
  ({ city }: { city: string }) => {
    return `The weather in ${city} is sunny.`;
  },
  {
    name: "get_weather",
    description: "Get the weather in a city.",
    schema: z.object({
      city: z.string(),
    }),
  },
);

let callCount = 0;

const logToolCallsMiddleware = createMiddleware({
  name: "LogToolCallsMiddleware",
  wrapToolCall: async (request, handler) => {
    // Intercept and log every tool call - demonstrates cross-cutting concern
    callCount += 1;
    const toolName = request.toolCall.name;

    console.log(`[Middleware] Tool call #${callCount}: ${toolName}`);
    console.log(
      `[Middleware] Arguments: ${JSON.stringify(request.toolCall.args)}`,
    );

    // Execute the tool call
    const result = await handler(request);

    // Log the result
    console.log(`[Middleware] Tool call #${callCount} completed`);

    return result;
  },
});

const agent = await createDeepAgent({
  model: "google_genai:gemini-3.1-pro-preview",
  tools: [getWeather] as any,
  middleware: [logToolCallsMiddleware] as any,
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
// :remove-end:

// :snippet-start: customization-middleware-do-js
const customMiddleware = createMiddleware({
  name: "CustomMiddleware",
  beforeAgent: async (state) => {
    return { x: (state.x ?? 0) + 1 }; // Update graph state instead
  },
});
// :snippet-end:

// :snippet-start: customization-middleware-dont-js
let x = 1;

const customMiddlewareBad = createMiddleware({
  name: "CustomMiddleware",
  beforeAgent: async () => {
    x += 1; // Mutation causes race conditions
  },
});
// :snippet-end:

// :remove-start:
if (!customMiddleware) throw new Error("middleware not created");
if (!customMiddlewareBad) throw new Error("middleware not created");
// :remove-end:
