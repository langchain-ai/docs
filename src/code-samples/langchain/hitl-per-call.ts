// :remove-start:
process.env.LANGSMITH_TRACING = "false";
process.env.OPENAI_API_KEY ??= "sk-test-key";
// :remove-end:

// :snippet-start: hitl-per-call-agent-js
import { MemorySaver } from "@langchain/langgraph";
import { createAgent, humanInTheLoopMiddleware, tool } from "langchain";
import * as z from "zod";

const writeFile = tool(
  ({ path, content }) => `Wrote ${content.length} characters to ${path}`,
  {
    name: "write_file",
    description: "Write content to a file.",
    schema: z.object({ path: z.string(), content: z.string() }),
  },
);

const executeSql = tool(() => "Deleted 42 rows", {
  name: "execute_sql",
  description: "Run a SQL query.",
  schema: z.object({ query: z.string() }),
});

const readData = tool(({ table }) => `3 rows from ${table}`, {
  name: "read_data",
  description: "Read rows from a table.",
  schema: z.object({ table: z.string() }),
});

let agent = createAgent({
  model: "openai:gpt-5.5",
  tools: [writeFile, executeSql, readData],
  middleware: [
    humanInTheLoopMiddleware({
      interruptOn: {
        write_file: true,
        execute_sql: { allowedDecisions: ["approve", "reject"] },
        read_data: false,
      },
      interruptMode: "per_call", // [!code highlight]
    }),
  ],
  checkpointer: new MemorySaver(),
});
// :snippet-end:

// :remove-start:
import assert from "node:assert/strict";
import { fakeModel } from "@langchain/core/testing";
import { AIMessage, ToolMessage } from "langchain";

const TOOL_CALLS = [
  {
    name: "write_file",
    args: { path: "orders_archive.csv", content: "id,total\n1,20\n" },
    id: "call_write",
  },
  {
    name: "execute_sql",
    args: { query: "DELETE FROM orders WHERE created_at < '2025-01-01'" },
    id: "call_sql",
  },
  { name: "read_data", args: { table: "orders" }, id: "call_read" },
];

// Asks for all three tools in one turn, then answers. One pair per thread.
const scripted = fakeModel();
for (let thread = 0; thread < 3; thread++) {
  scripted.respondWithTools(TOOL_CALLS).respond(new AIMessage("Done."));
}

agent = createAgent({
  model: scripted,
  tools: [writeFile, executeSql, readData],
  middleware: [
    humanInTheLoopMiddleware({
      interruptOn: {
        write_file: true,
        execute_sql: { allowedDecisions: ["approve", "reject"] },
        read_data: false,
      },
      interruptMode: "per_call",
    }),
  ],
  checkpointer: new MemorySaver(),
});

function toolResults(state: { messages: unknown[] }) {
  return Object.fromEntries(
    state.messages
      .filter((message) => ToolMessage.isInstance(message))
      .map((message) => [message.name, [message.status, message.content]]),
  );
}

const originalLog = console.log;
const printed: unknown[] = [];
console.log = (value: unknown) => printed.push(value);
// :remove-end:

// :snippet-start: hitl-per-call-invoke-js
import { isToolApprovalInterrupt } from "langchain";

let config = { configurable: { thread_id: "1" } };
let result = await agent.invoke(
  {
    messages: [
      { role: "user", content: "Archive old orders, then delete them." },
    ],
  },
  config,
);

// One interrupt per gated tool call, in no fixed order
const approvals = (result.__interrupt__ ?? []).filter(isToolApprovalInterrupt);
for (const interrupt of approvals) {
  console.log(interrupt.value);
}
// > {
// >   type: 'tool_approval',
// >   tool_call_id: 'call_write',
// >   name: 'write_file',
// >   args: { path: 'orders_archive.csv', content: 'id,total\n1,20\n' },
// >   description: 'Tool execution requires approval\n\nTool: write_file\nArgs: {\n  "path": "orders_archive.csv",\n  "content": "id,total\\n1,20\\n"\n}'
// > }
// > {
// >   type: 'tool_approval',
// >   tool_call_id: 'call_sql',
// >   name: 'execute_sql',
// >   args: { query: "DELETE FROM orders WHERE created_at < '2025-01-01'" },
// >   description: `Tool execution requires approval\n\nTool: execute_sql\nArgs: {\n  "query": "DELETE FROM orders WHERE created_at < '2025-01-01'"\n}`
// > }
// :snippet-end:

// :remove-start:
console.log = originalLog;
const byName = (values: unknown[]) =>
  [...(values as { name: string }[])].sort((a, b) =>
    b.name.localeCompare(a.name),
  );
assert.deepEqual(byName(printed), [
  {
    type: "tool_approval",
    tool_call_id: "call_write",
    name: "write_file",
    args: { path: "orders_archive.csv", content: "id,total\n1,20\n" },
    description:
      'Tool execution requires approval\n\nTool: write_file\nArgs: {\n  "path": "orders_archive.csv",\n  "content": "id,total\\n1,20\\n"\n}',
  },
  {
    type: "tool_approval",
    tool_call_id: "call_sql",
    name: "execute_sql",
    args: { query: "DELETE FROM orders WHERE created_at < '2025-01-01'" },
    description:
      "Tool execution requires approval\n\nTool: execute_sql\nArgs: {\n  \"query\": \"DELETE FROM orders WHERE created_at < '2025-01-01'\"\n}",
  },
]);
// `read_data` isn't gated, so it ran without waiting for the review.
assert.deepEqual(toolResults(result), {
  read_data: ["success", "3 rows from orders"],
});
// One branch per allowed decision, matched on `type`.
const branchTypes = (name: string) =>
  (
    approvals.find((interrupt) => interrupt.value.name === name)!
      .response_schema as { oneOf: { properties: { type: { const: string } } }[] }
  ).oneOf.map((branch) => branch.properties.type.const);
assert.deepEqual(branchTypes("write_file"), ["approve", "edit", "reject"]);
assert.deepEqual(branchTypes("execute_sql"), ["approve", "reject"]);
// :remove-end:

// :snippet-start: hitl-per-call-resume-js
import { Command } from "@langchain/langgraph";

const decisions = Object.fromEntries(
  approvals.map((interrupt) => [
    interrupt.id,
    interrupt.value.name === "execute_sql"
      ? { type: "reject", message: "Archive the rows before deleting them." }
      : { type: "approve" },
  ]),
);

result = await agent.invoke(new Command({ resume: decisions }), config);
// :snippet-end:

// :remove-start:
assert.equal(result.__interrupt__, undefined);
assert.deepEqual(toolResults(result), {
  read_data: ["success", "3 rows from orders"],
  write_file: ["success", "Wrote 14 characters to orders_archive.csv"],
  execute_sql: ["error", "Archive the rows before deleting them."],
});

config = { configurable: { thread_id: "2" } };
result = await agent.invoke(
  {
    messages: [
      { role: "user", content: "Archive old orders, then delete them." },
    ],
  },
  config,
);
console.log = (value: unknown) => printed.push(value);
printed.length = 0;
// :remove-end:

// :snippet-start: hitl-per-call-invalid-js
const writeFileInterrupt = (result.__interrupt__ ?? [])
  .filter(isToolApprovalInterrupt)
  .find((interrupt) => interrupt.value.name === "write_file")!;
const args: Record<string, string> = { path: "archive/orders_2024.csv" };
const edit = { type: "edit", edited_action: { name: "write_file", args } };

try {
  await agent.invoke(
    new Command({ resume: { [writeFileInterrupt.id]: edit } }),
    config,
  );
} catch (error) {
  // The middleware wraps the error; its `cause` lists what failed
  if (!(error instanceof Error && error.cause instanceof z.core.$ZodError)) {
    throw error;
  }
  for (const issue of error.cause.issues) {
    console.log(`${issue.path.join(".")} ${issue.message}`);
  }
}
// > edited_action.args.content Invalid input: expected string, received undefined

// Nothing was saved, so answer the same interrupt again
args.content = "id,total\n1,20\n";
result = await agent.invoke(
  new Command({ resume: { [writeFileInterrupt.id]: edit } }),
  config,
);
// :snippet-end:

// :remove-start:
console.log = originalLog;
assert.deepEqual(printed, [
  "edited_action.args.content Invalid input: expected string, received undefined",
]);
// The corrected edit ran; `execute_sql` is still waiting for its own answer.
const pending = (result.__interrupt__ ?? []).filter(isToolApprovalInterrupt);
assert.deepEqual(
  pending.map((interrupt) => interrupt.value.name),
  ["execute_sql"],
);
assert.deepEqual(toolResults(result).write_file, [
  "success",
  "Note: a human reviewer replaced this tool call before it ran. The call recorded in your message is the one you produced, not the one that executed. This was intentional and authorized. Do not re-issue your original call. Executed instead: write_file with arguments " +
    '{"path":"archive/orders_2024.csv","content":"id,total\\n1,20\\n"}.\n\n' +
    "Tool response:\nWrote 14 characters to archive/orders_2024.csv",
]);
result = await agent.invoke(
  new Command({ resume: { [pending[0].id]: { type: "approve" } } }),
  config,
);
assert.deepEqual(toolResults(result).execute_sql, [
  "success",
  "Deleted 42 rows",
]);

config = { configurable: { thread_id: "3" } };
let stream = await agent.streamEvents(
  {
    messages: [
      { role: "user", content: "Archive old orders, then delete them." },
    ],
  },
  { ...config, version: "v3" },
);
for await (const message of stream.messages) {
  for await (const _token of message.text) {
    // Drain the stream so the run reaches the interrupts.
  }
}
assert.ok(stream.interrupted);
assert.equal(stream.interrupts.length, 2);
const tokens: string[] = [];
const write = process.stdout.write.bind(process.stdout);
process.stdout.write = ((token: string) => tokens.push(token)) as never;
// :remove-end:

// :snippet-start: hitl-per-call-stream-js
const streamDecisions = Object.fromEntries(
  stream.interrupts.map((interrupt) => [
    interrupt.interruptId,
    { type: "approve" },
  ]),
);
stream = await agent.streamEvents(new Command({ resume: streamDecisions }), {
  ...config,
  version: "v3",
});
for await (const message of stream.messages) {
  for await (const token of message.text) {
    process.stdout.write(token);
  }
}
// :snippet-end:

// :remove-start:
process.stdout.write = write;
assert.equal(tokens.join(""), "Done.");
assert.ok(!stream.interrupted);
assert.deepEqual(toolResults(await stream.output).execute_sql, [
  "success",
  "Deleted 42 rows",
]);
console.log(
  "✓ per-call interrupts: invoke, resume by ID, invalid answer, streaming",
);
// :remove-end:
