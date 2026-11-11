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
    // GPT-6 models need the Responses API for tool calling in @langchain/openai.
    const model = await initChatModel(
      modelName,
      /(?:^|:)gpt-6/.test(modelName) ? { useResponsesApi: true } : undefined,
    );
    return handler({ ...request, model });
  },
});

// KEEP MODEL
const agent = await createDeepAgent({
  model: "google:gemini-3.6-flash",
  middleware: [configurableModel],
  contextSchema,
});

// Invoke with the user's model selection
const result = await agent.invoke(
  { messages: [{ role: "user", content: "Hello!" }] },
  // KEEP MODEL
  { context: { model: "openai:gpt-6.1-sol" } },
);
// :snippet-end:
