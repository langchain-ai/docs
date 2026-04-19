// :snippet-start: middleware-dynamic-prompt-js
import { createMiddleware, SystemMessage, createAgent } from "langchain";

const addContextMiddleware = createMiddleware({
  name: "AddContextMiddleware",
  wrapModelCall: async (request, handler) => {
    return handler({
      ...request,
      systemMessage: request.systemMessage.concat(`Additional context.`),
    });
  },
});

const agent = createAgent({
  model: "gpt-4.1",
  systemPrompt: "You are a helpful assistant.",
  middleware: [addContextMiddleware],
});
// :snippet-end:

// :remove-start:
import { FakeListChatModel } from "@langchain/core/utils/testing";
import type { BaseMessage } from "@langchain/core/messages";

function flattenMessageContent(content: unknown): string {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .map((block) => {
        if (typeof block === "string") return block;
        if (block && typeof block === "object" && "text" in block) {
          return String((block as { text?: unknown }).text ?? "");
        }
        return "";
      })
      .join("");
  }
  return "";
}

async function assertMiddlewareAddsContextToSystemPrompt(
  middleware: typeof addContextMiddleware,
) {
  let modelMessages: BaseMessage[] = [];

  const model = new FakeListChatModel({ responses: ["ok"] });
  const testAgent = createAgent({
    model,
    tools: [],
    systemPrompt: "You are a helpful assistant.",
    middleware: [middleware],
  });
  await testAgent.invoke(
    { messages: [{ role: "user", content: "Hello" }] },
    {
      callbacks: [
        {
          handleChatModelStart(_llm, messages) {
            modelMessages = messages[0] ?? [];
          },
        },
      ],
    },
  );

  if (modelMessages.length === 0) {
    throw new Error("expected the model to be called once");
  }
  const systemMsg = modelMessages.find((m) => m.type === "system");
  if (!systemMsg) {
    throw new Error("expected a system message in model input");
  }
  const systemText = flattenMessageContent(systemMsg.content);
  if (!systemText.includes("You are a helpful assistant.")) {
    throw new Error(`expected base system prompt, got: ${systemText}`);
  }
  if (!systemText.includes("Additional context.")) {
    throw new Error(`expected middleware context, got: ${systemText}`);
  }
}

async function main() {
  if (!addContextMiddleware) {
    throw new Error("addContextMiddleware should be defined");
  }
  if (!agent) {
    throw new Error("agent should be defined");
  }

  await assertMiddlewareAddsContextToSystemPrompt(addContextMiddleware);
  console.log("✓ AddContextMiddleware adds context to the model request");

  const contextMiddleware = createMiddleware({
    name: "ContextMiddleware",
    wrapModelCall: async (request, handler) => {
      return handler({
        ...request,
        systemMessage: request.systemMessage.concat(`Additional context.`),
      });
    },
  });
  await assertMiddlewareAddsContextToSystemPrompt(contextMiddleware);
  console.log("✓ ContextMiddleware adds context to the model request");
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
// :remove-end:
