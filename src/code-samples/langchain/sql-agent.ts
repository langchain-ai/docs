/** Build a SQL agent with LangChain tools. */

// :snippet-start: sql-agent-download-chinook-js
import fs from "node:fs/promises";
import path from "node:path";

const url =
  "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db";
const localPath = path.resolve("Chinook.db");

async function resolveDbPath() {
  try {
    await fs.access(localPath);
    return localPath;
  } catch {
    // Chinook.db not present locally; download it.
  }
  const resp = await fetch(url);
  if (!resp.ok)
    throw new Error(`Failed to download DB. Status code: ${resp.status}`);
  const buf = Buffer.from(await resp.arrayBuffer());
  await fs.writeFile(localPath, buf);
  return localPath;
}
// :snippet-end:

// :snippet-start: sql-agent-run-query-js
import sqlite3 from "sqlite3";

// Below are minimal tools for demonstration purposes.
async function runQuery(query: string): Promise<any[]> {
  const dbPath = await resolveDbPath();
  const db = new sqlite3.Database(dbPath);
  return new Promise((resolve, reject) => {
    db.all(query, [], (err, rows) => {
      db.close();
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

async function getSchema() {
  const tables = await runQuery(
    "SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';",
  );
  return tables.map((row) => row.sql).join("\n\n");
}
// :snippet-end:

// :snippet-start: sql-agent-sanitize-sql-js
const DENY_RE =
  /\b(INSERT|UPDATE|DELETE|ALTER|DROP|CREATE|REPLACE|TRUNCATE)\b/i;
const HAS_LIMIT_TAIL_RE = /\blimit\b\s+\d+(\s*,\s*\d+)?\s*;?\s*$/i;

function sanitizeSqlQuery(q) {
  let query = String(q ?? "").trim();

  // block multiple statements (allow one optional trailing ;)
  const semis = [...query].filter((c) => c === ";").length;
  if (semis > 1 || (query.endsWith(";") && query.slice(0, -1).includes(";"))) {
    throw new Error("multiple statements are not allowed.");
  }
  query = query.replace(/;+\s*$/g, "").trim();

  // read-only gate
  if (!query.toLowerCase().startsWith("select")) {
    throw new Error("Only SELECT statements are allowed");
  }
  if (DENY_RE.test(query)) {
    throw new Error("DML/DDL detected. Only read-only queries are permitted.");
  }

  // append LIMIT only if not already present
  if (!HAS_LIMIT_TAIL_RE.test(query)) {
    query += " LIMIT 5";
  }
  return query;
}
// :snippet-end:

// :snippet-start: sql-agent-execute-sql-js
import { tool } from "langchain";
import * as z from "zod";

const executeSql = tool(
  async ({ query }) => {
    const q = sanitizeSqlQuery(query);
    try {
      const result = await runQuery(q);
      return JSON.stringify(result, null, 2);
    } catch (e) {
      const message = e instanceof Error ? e.message : String(e);
      throw new Error(message);
    }
  },
  {
    name: "execute_sql",
    description: "Execute a READ-ONLY SQLite SELECT query and return results.",
    schema: z.object({
      query: z.string().describe("SQLite SELECT query to execute (read-only)."),
    }),
  },
);
// :snippet-end:

// :snippet-start: sql-agent-system-prompt-js
import { SystemMessage } from "langchain";

const getSystemPrompt = async () =>
  new SystemMessage(`You are a careful SQLite analyst.

Authoritative schema (do not invent columns/tables):
${await getSchema()}

Rules:
- Think step-by-step.
- When you need data, call the tool \`execute_sql\` with ONE SELECT query.
- Read-only only; no INSERT/UPDATE/DELETE/ALTER/DROP/CREATE/REPLACE/TRUNCATE.
- Limit to 5 rows unless user explicitly asks otherwise.
- If the tool returns 'Error:', revise the SQL and try again.
- Limit the number of attempts to 5.
- If you are not successful after 5 attempts, return a note to the user.
- Prefer explicit column lists; avoid SELECT *.
`);
// :snippet-end:

// :snippet-start: sql-agent-create-agent-js
import { createAgent } from "langchain";

let agent = createAgent({
  model: "gpt-5.5",
  tools: [executeSql],
  systemPrompt: await getSystemPrompt(),
});
// :snippet-end:

// :snippet-start: sql-agent-run-agent-js
let question = "Which genre, on average, has the longest tracks?";

for await (const step of await agent.stream(
  { messages: [{ role: "user", content: question }] },
  { streamMode: "values" },
)) {
  const message = step.messages.at(-1);
  console.log(`${message.role}: ${JSON.stringify(message.content, null, 2)}`);
}
// :snippet-end:

// :snippet-start: sql-agent-hitl-middleware-js
import { createAgent, humanInTheLoopMiddleware } from "langchain"; // [!code highlight]
import { MemorySaver } from "@langchain/langgraph"; // [!code highlight]

agent = createAgent({
  model: "gpt-5.5",
  tools: [executeSql],
  systemPrompt: await getSystemPrompt(),
  middleware: [
    // [!code highlight]
    humanInTheLoopMiddleware({
      // [!code highlight]
      interruptOn: {
        execute_sql: true, // [!code highlight]
      },
      descriptionPrefix: "Tool execution pending approval", // [!code highlight]
    }),
  ], // [!code highlight]
  checkpointer: new MemorySaver(), // [!code highlight]
});
// :snippet-end:

// :snippet-start: sql-agent-hitl-run-js
question = "Which genre, on average, has the longest tracks?";
const config = { configurable: { thread_id: "1" } }; // [!code highlight]

for await (const step of await agent.stream(
  { messages: [{ role: "user", content: question }] },
  { ...config, streamMode: "values" }, // [!code highlight]
)) {
  if ("__interrupt__" in step) {
    // [!code highlight]
    console.log("INTERRUPTED:"); // [!code highlight]
    for (const interrupt of step.__interrupt__) {
      // [!code highlight]
      for (const request of interrupt.value.actionRequests) {
        // [!code highlight]
        console.log(request.description); // [!code highlight]
      }
    }
  } else if (step.messages) {
    const message = step.messages.at(-1);
    console.log(`${message.role}: ${JSON.stringify(message.content, null, 2)}`);
  }
}
// :snippet-end:

// :snippet-start: sql-agent-hitl-resume-js
import { Command } from "@langchain/langgraph"; // [!code highlight]

for await (const step of await agent.stream(
  new Command({ resume: { decisions: [{ type: "approve" }] } }), // [!code highlight]
  { ...config, streamMode: "values" },
)) {
  if (step.messages) {
    const message = step.messages.at(-1);
    console.log(`${message.role}: ${JSON.stringify(message.content, null, 2)}`);
  }
  if ("__interrupt__" in step) {
    console.log("INTERRUPTED:");
    for (const interrupt of step.__interrupt__) {
      for (const request of interrupt.value.actionRequests) {
        console.log(request.description);
      }
    }
  }
}
// :snippet-end:

// :remove-start:
async function main() {
  const dbPath = await resolveDbPath();
  const stat = await fs.stat(dbPath);
  if (stat.size <= 0) {
    throw new Error("Chinook.db is empty");
  }

  const schema = await getSchema();
  if (!schema.includes("CREATE TABLE")) {
    throw new Error("Expected CREATE TABLE in schema output");
  }

  const sanitized = sanitizeSqlQuery("SELECT Name FROM Artist");
  if (!sanitized.endsWith("LIMIT 5")) {
    throw new Error(`Expected LIMIT appended, got: ${sanitized}`);
  }

  try {
    sanitizeSqlQuery("DELETE FROM Artist");
    throw new Error("Expected sanitizeSqlQuery to reject DELETE");
  } catch (e) {
    if (!(e instanceof Error) || !e.message.includes("SELECT")) {
      throw e;
    }
  }

  const result = await executeSql.invoke({
    query: "SELECT Name FROM Artist LIMIT 1",
  });
  if (!result.includes("Artist") && !result.includes("Name")) {
    throw new Error(`Unexpected execute_sql result: ${result}`);
  }

  const prompt = await getSystemPrompt();
  const text =
    typeof prompt.content === "string"
      ? prompt.content
      : JSON.stringify(prompt.content);
  if (!text.includes("CREATE TABLE")) {
    throw new Error("Expected schema in system prompt");
  }

  if (!agent) {
    throw new Error("Agent creation failed");
  }

  console.log("✓ sql-agent");
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
// :remove-end:
