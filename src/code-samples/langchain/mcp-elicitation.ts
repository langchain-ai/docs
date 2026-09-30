// :snippet-start: mcp-elicitation-js
import { Command, MemorySaver } from "@langchain/langgraph";
import {
  MCPAdapter,
  createMCPElicitationResume,
  type MCPElicitationInterrupt,
} from "@langchain/mcp-adapters";
import { createAgent } from "langchain";

async function bookWithElicitation(serverUrl: string) {
  // When a server needs input mid-call, the adapter surfaces the question
  // as a LangGraph interrupt.
  const adapter = new MCPAdapter({
    servers: { booking: { url: serverUrl } },
  });

  try {
    const tools = await adapter.listTools();
    // :remove-start:
    await validateTools(tools);
    // :remove-end:
    // A checkpointer saves the interrupted run so it can resume.
    const agent = createAgent({
      // KEEP MODEL
      model: "claude-sonnet-5-5",
      tools,
      checkpointer: new MemorySaver(),
    });
    // :remove-start:
    assert.ok(agent);
    if (!process.env.ANTHROPIC_API_KEY) {
      console.log(
        "Agent constructed; model invocation not tested (no ANTHROPIC_API_KEY).",
      );
      return;
    }
    // :remove-end:
    const config = { configurable: { thread_id: "booking-1" } };

    const paused = await agent.invoke(
      { messages: [{ role: "user", content: "Book a table for 4." }] },
      config,
    );
    const [pending] = paused.__interrupt__!;
    const question = pending.value as MCPElicitationInterrupt;
    const [key] = Object.keys(question.requests);

    // Answers are keyed by the server's own request key.
    // Use `decline` or `cancel` to refuse the request.
    const answer = {
      action: "accept" as const,
      content: { date: "2026-09-14" },
    };
    // Address the answer to the interrupt that requested it.
    const resume = createMCPElicitationResume(pending, { [key]: answer });
    return await agent.invoke(new Command({ resume }), config);
  } finally {
    await adapter.close();
  }
}
// :snippet-end:

// :remove-start:
import assert from "node:assert/strict";
import { once } from "node:events";
import { createServer } from "node:http";
import { toNodeHandler } from "@modelcontextprotocol/node";
import {
  createMcpHandler,
  McpServer,
  inputRequired,
} from "@modelcontextprotocol/server";
import { z } from "zod/v4";
import { MessagesAnnotation, StateGraph } from "@langchain/langgraph";
import { ToolNode } from "@langchain/langgraph/prebuilt";
import { AIMessage } from "langchain";

async function validateTools(
  tools: Awaited<ReturnType<MCPAdapter["listTools"]>>,
) {
  const graph = new StateGraph(MessagesAnnotation)
    .addNode("tools", new ToolNode(tools))
    .addEdge("__start__", "tools")
    .addEdge("tools", "__end__")
    .compile({ checkpointer: new MemorySaver() });
  const config = { configurable: { thread_id: "elicitation-fixture" } };
  await graph.invoke(
    {
      messages: [
        new AIMessage({
          content: "",
          tool_calls: [
            { id: "booking-1", name: tools[0].name, args: { party_size: 4 } },
          ],
        }),
      ],
    },
    config,
  );
  const paused = await graph.getState(config);
  const [pending] = paused.tasks.flatMap((task) => task.interrupts);
  assert.ok(pending);
  const question = pending.value as MCPElicitationInterrupt;
  assert.deepEqual(Object.keys(question.requests), ["date"]);
  const answer = { action: "accept" as const, content: { date: "2026-09-14" } };
  const resumed = await graph.invoke(
    new Command({
      resume: createMCPElicitationResume(pending, { date: answer }),
    }),
    config,
  );
  const completed = await graph.getState(config);
  assert.equal(completed.tasks.flatMap((task) => task.interrupts).length, 0);
  assert.match(
    resumed.messages.at(-1)!.text,
    /Booked a table for 4 on 2026-09-14/,
  );
}

const handler = createMcpHandler(
  () => {
    const server = new McpServer({ name: "fixture", version: "1" });
    server.registerTool(
      "book_table",
      { inputSchema: z.object({ party_size: z.number() }) },
      ({ party_size }, context) => {
        const answer = context.mcpReq.inputResponses?.date;
        if (!answer) {
          return inputRequired({
            requestState: "awaiting-date",
            inputRequests: {
              date: inputRequired.elicit({
                message: "What date would you like to book?",
                requestedSchema: {
                  type: "object",
                  properties: { date: { type: "string", format: "date" } },
                  required: ["date"],
                },
              }),
            },
          });
        }
        assert.equal(context.mcpReq.requestState(), "awaiting-date");
        const response = z
          .object({
            action: z.enum(["accept", "decline", "cancel"]),
            content: z.object({ date: z.string() }).optional(),
          })
          .parse(answer);
        if (response.action !== "accept" || !response.content) {
          return {
            content: [
              { type: "text", text: "No date given, so nothing was booked." },
            ],
          };
        }
        const date = response.content.date;
        return {
          content: [
            {
              type: "text",
              text: `Booked a table for ${party_size} on ${date}.`,
            },
          ],
        };
      },
    );
    return server;
  },
  { legacy: "reject" },
);
const http = createServer(toNodeHandler(handler));
http.listen(0, "127.0.0.1");
await once(http, "listening");
const address = http.address();
assert.ok(address && typeof address !== "string");
try {
  await bookWithElicitation(`http://127.0.0.1:${address.port}/mcp`);
  console.log("✓ mcp-elicitation: local MCP validation passed");
} finally {
  await handler.close();
  const closed = once(http, "close");
  http.close();
  http.closeAllConnections();
  await closed;
}
// :remove-end:
