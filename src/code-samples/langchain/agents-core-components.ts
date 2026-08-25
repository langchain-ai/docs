// Agents docs: core component examples (intro, model, tools, system prompt, structured output, name).

// :remove-start:
// Shared tools placeholder for snippets that reference `tools`.
var tools = [];
// :remove-end:

// :snippet-start: agents-intro-js
import { createAgent } from "langchain";

var agent = createAgent({ model: "openai:gpt-5.4", tools });
// :snippet-end:

// :remove-start:
const introAgent = agent;
// :remove-end:

// :snippet-start: agents-tools-js
import { tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Results for: ${query}`, {
  name: "search",
  description: "Search for information",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({ model: "openai:gpt-5.4", tools: [search] });
// :snippet-end:

// :remove-start:
const toolsAgent = agent;
// :remove-end:

// :snippet-start: agents-system-prompt-js
var agent = createAgent({
  model: "openai:gpt-5.4",
  tools,
  systemPrompt: "You are a helpful assistant. Be concise and accurate.",
});
// :snippet-end:

// :remove-start:
const systemPromptAgent = agent;
// :remove-end:

// :snippet-start: agents-structured-output-js
const Answer = z.object({ summary: z.string(), confidence: z.number() });

var agent = createAgent({
  model: "openai:gpt-5.4",
  tools,
  responseFormat: Answer,
});
const result = await agent.invoke({
  messages: [{ role: "user", content: "Summarize AI trends" }],
});
result.structuredResponse; // { summary: ..., confidence: ... }
// :snippet-end:

// :remove-start:
const structuredOutputAgent = agent;
const structuredOutputResult = result;
// :remove-end:

// :snippet-start: agents-name-js
var agent = createAgent({
  model: "openai:gpt-5.4",
  tools,
  name: "research_assistant",
});
// :snippet-end:

// :remove-start:
import { AIMessage } from "@langchain/core/messages";

const nameAgent = agent;

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

async function assertInvokes(
  testAgent: typeof agent,
  label: string,
): Promise<void> {
  const invokeResult = await testAgent.invoke({
    messages: [{ role: "user", content: "Say hello in one short sentence." }],
  });
  if (!assistantText(invokeResult).trim()) {
    throw new Error(`${label}: expected non-empty reply`);
  }
  console.log(`✓ ${label}`);
}

async function main() {
  await assertInvokes(introAgent, "agents intro");
  await assertInvokes(toolsAgent, "agents tools");
  await assertInvokes(systemPromptAgent, "agents system prompt");
  const structured = structuredOutputResult.structuredResponse;
  if (!structured?.summary?.trim()) {
    throw new Error("expected structured summary");
  }
  if (structured.confidence < 0 || structured.confidence > 1) {
    throw new Error("expected confidence in [0, 1]");
  }
  console.log("✓ agents structured output");
  await assertInvokes(nameAgent, "agents name");
}

main();
// :remove-end:
