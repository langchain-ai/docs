// :snippet-start: middleware-dynamic-model-selection-js
import { createMiddleware, initChatModel } from "langchain";

const models = {
  complex: await initChatModel("claude-sonnet-4-6"),
  simple: await initChatModel("claude-haiku-4-5-20251001"),
};

const dynamicModelMiddleware = createMiddleware({
  name: "DynamicModelMiddleware",
  wrapModelCall: (request, handler) => {
    const modifiedRequest = { ...request };
    if (request.messages.length > 10) {
      modifiedRequest.model = models.complex;
    } else {
      modifiedRequest.model = models.simple;
    }
    return handler(modifiedRequest);
  },
});
// :snippet-end:

// :remove-start:
import { createAgent } from "langchain";
import { FakeListChatModel } from "@langchain/core/utils/testing";

async function assertModelRoutesByMessageCount(
  middleware: typeof dynamicModelMiddleware,
): Promise<void> {
  const simpleFake = new FakeListChatModel({
    responses: ["__lc_simple_route__"],
  });
  const complexFake = new FakeListChatModel({
    responses: ["__lc_complex_route__"],
  });
  const placeholder = new FakeListChatModel({
    responses: ["__lc_placeholder__"],
  });

  Object.assign(models, { simple: simpleFake, complex: complexFake });

  const agent = createAgent({
    model: placeholder,
    tools: [],
    middleware: [middleware],
  });

  let serialized = "";
  await agent.invoke(
    { messages: [{ role: "user", content: "Short thread." }] },
    {
      callbacks: [
        {
          handleChatModelStart(llm) {
            serialized = JSON.stringify(llm);
          },
        },
      ],
    },
  );

  if (!serialized.includes("__lc_simple_route__")) {
    throw new Error(
      `expected simple model when the request has at most 10 messages, got: ${serialized}`,
    );
  }
  if (serialized.includes("__lc_complex_route__")) {
    throw new Error("did not expect complex model for a short thread");
  }

  serialized = "";
  const longThread = Array.from({ length: 11 }, (_, i) => ({
    role: "user" as const,
    content: `msg-${i}`,
  }));
  await agent.invoke(
    { messages: longThread },
    {
      callbacks: [
        {
          handleChatModelStart(llm) {
            serialized = JSON.stringify(llm);
          },
        },
      ],
    },
  );

  if (!serialized.includes("__lc_complex_route__")) {
    throw new Error(
      `expected complex model when the request has more than 10 messages, got: ${serialized}`,
    );
  }
  if (serialized.includes("__lc_simple_route__")) {
    throw new Error("did not expect simple model for a long thread");
  }
}

async function main(): Promise<void> {
  if (!dynamicModelMiddleware) {
    throw new Error("dynamicModelMiddleware should be defined");
  }

  await assertModelRoutesByMessageCount(dynamicModelMiddleware);
  console.log(
    "✓ DynamicModelMiddleware routes to the expected model by message count",
  );

  const dynamicModelMiddlewareAlt = createMiddleware({
    name: "DynamicModelMiddlewareAlt",
    wrapModelCall: (request, handler) => {
      const modifiedRequest = { ...request };
      if (request.messages.length > 10) {
        modifiedRequest.model = models.complex;
      } else {
        modifiedRequest.model = models.simple;
      }
      return handler(modifiedRequest);
    },
  });
  await assertModelRoutesByMessageCount(dynamicModelMiddlewareAlt);
  console.log(
    "✓ Equivalent inline middleware routes to the expected model by message count",
  );
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
// :remove-end:
