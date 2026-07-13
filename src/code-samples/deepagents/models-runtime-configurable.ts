// :snippet-start: models-runtime-configurable-js
import { createMiddleware, initChatModel } from "langchain";
import { createDeepAgent } from "deepagents";
import * as z from "zod";

const contextSchema = z.object({
  model: z.string(),
});

const configurableModel = createMiddleware({
  name: "ConfigurableModel",
  wrapModelCall: async (request, handler) => {
    const modelName = request.runtime.context.model;
    const model = await initChatModel(modelName);
    return handler({ ...request, model });
  },
});

// KEEP MODEL
const agent = await createDeepAgent({
  model: "google-genai:gemini-3.5-flash",
  middleware: [configurableModel],
  contextSchema,
});

// Invoke with the user's model selection
const result = await agent.invoke(
  { messages: [{ role: "user", content: "Hello!" }] },
  // KEEP MODEL
  { context: { model: "openai:gpt-5.5" } },
);
// :snippet-end:
