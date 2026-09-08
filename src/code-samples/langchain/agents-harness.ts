// Agents docs: harness examples (execution environment, context management, middleware).

// :remove-start:
import { tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Results for: ${query}`, {
  name: "search",
  description: "Search for information",
  schema: z.object({ query: z.string() }),
});
// :remove-end:

// :snippet-start: agents-execution-environment-js
import { createAgent } from "langchain";
import { createFilesystemMiddleware, StateBackend } from "deepagents";

var agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [search],
  middleware: [createFilesystemMiddleware({ backend: new StateBackend() })],
});
// :snippet-end:

// :remove-start:
const executionEnvironmentAgent = agent;
// :remove-end:

// :snippet-start: agents-context-management-js
import { createAgent } from "langchain";
import {
  StateBackend,
  createFilesystemMiddleware,
  createSkillsMiddleware,
  createSummarizationMiddleware,
} from "deepagents";

var backend = new StateBackend();
const model = "anthropic:claude-sonnet-4-6";

var agent = createAgent({
  model,
  tools: [search],
  middleware: [
    createFilesystemMiddleware({ backend }),
    createSummarizationMiddleware({ model, backend }),
    createSkillsMiddleware({ backend, sources: ["./skills/"] }),
  ],
});
// :snippet-end:

// :remove-start:
const contextManagementAgent = agent;
// :remove-end:

// :snippet-start: agents-fault-tolerance-js
import {
  createAgent,
  modelRetryMiddleware,
  tool,
  toolRetryMiddleware,
} from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [search],
  middleware: [
    modelRetryMiddleware({ maxRetries: 3 }),
    toolRetryMiddleware({ maxRetries: 2 }),
  ],
});
// :snippet-end:

// :remove-start:
const faultToleranceAgent = agent;
// :remove-end:

// :snippet-start: agents-guardrails-js
import { createAgent, piiMiddleware, tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [search],
  middleware: [piiMiddleware("email")],
});
// :snippet-end:

// :remove-start:
const guardrailsAgent = agent;
// :remove-end:

// :snippet-start: agents-planning-delegation-js
import { createAgent, todoListMiddleware, tool } from "langchain";
import {
  createFilesystemMiddleware,
  createSubAgentMiddleware,
  StateBackend,
} from "deepagents";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var backend = new StateBackend();

var agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [search],
  middleware: [
    createFilesystemMiddleware({ backend }),
    todoListMiddleware(),
    createSubAgentMiddleware({
      defaultModel: "anthropic:claude-sonnet-4-6",
      defaultTools: [],
      subagents: [
        {
          name: "researcher",
          description: "Searches and returns a structured summary.",
          systemPrompt:
            "Use the search tool to research the question and summarize key points.",
          tools: [search],
          model: "anthropic:claude-sonnet-4-6",
          middleware: [],
        },
      ],
    }),
  ],
});
// :snippet-end:

// :remove-start:
const planningDelegationAgent = agent;
// :remove-end:

// :snippet-start: agents-steering-js
import { createAgent, humanInTheLoopMiddleware, tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [search],
  middleware: [humanInTheLoopMiddleware({ interruptOn: { writeFile: true } })],
});
// :snippet-end:

// :remove-start:
import { AIMessage } from "@langchain/core/messages";

const steeringAgent = agent;

function assistantText(result: { messages: unknown[] }): string {
  const last = result.messages[result.messages.length - 1];
  if (!(last instanceof AIMessage)) {
    throw new Error("expected final assistant message");
  }
  const blocks = last.contentBlocks ?? [];
  const textBlock = blocks.find((b) => b.type === "text");
  if (textBlock && textBlock.type === "text") {
    return textBlock.text;
  }
  return typeof last.content === "string" ? last.content : "";
}

async function assertAgentInvokes(
  testAgent: typeof agent,
  label: string,
): Promise<void> {
  const result = await testAgent.invoke({
    messages: [
      {
        role: "user",
        content: "Use the search tool to look up LangChain agents.",
      },
    ],
  });
  if (!assistantText(result).trim()) {
    throw new Error(`${label}: expected non-empty assistant reply`);
  }
  console.log(`✓ ${label} invokes and returns a response`);
}

async function main() {
  await assertAgentInvokes(
    executionEnvironmentAgent,
    "agents execution environment",
  );
  await assertAgentInvokes(contextManagementAgent, "agents context management");
  await assertAgentInvokes(faultToleranceAgent, "agents fault tolerance");
  await assertAgentInvokes(guardrailsAgent, "agents guardrails");
  await assertAgentInvokes(
    planningDelegationAgent,
    "agents planning/delegation",
  );
  await assertAgentInvokes(steeringAgent, "agents steering");
}

main();
// :remove-end:
