/** Studio entrypoint for the SQL agent tutorial (`sqlAgent.ts`). */

// :snippet-start: sql-agent-studio-js
import fs from "node:fs/promises";
import path from "node:path";
import sqlite3 from "sqlite3";
import { SystemMessage, createAgent, tool } from "langchain";
import * as z from "zod";

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

// Below are minimal tools for demonstration purposes.
async function runQuery(query: string): Promise<Record<string, unknown>[]> {
  const dbPath = await resolveDbPath();
  const db = new sqlite3.Database(dbPath);
  return new Promise((resolve, reject) => {
    db.all(query, [], (err, rows) => {
      db.close();
      if (err) reject(err);
      else resolve(rows as Record<string, unknown>[]);
    });
  });
}

async function getSchema() {
  const tables = await runQuery(
    "SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';",
  );
  return tables.map((row) => String(row.sql)).join("\n\n");
}

const DENY_RE =
  /\b(INSERT|UPDATE|DELETE|ALTER|DROP|CREATE|REPLACE|TRUNCATE)\b/i;
const HAS_LIMIT_TAIL_RE = /\blimit\b\s+\d+(\s*,\s*\d+)?\s*;?\s*$/i;

function sanitizeSqlQuery(q: string) {
  let query = String(q ?? "").trim();

  const semis = [...query].filter((c) => c === ";").length;
  if (semis > 1 || (query.endsWith(";") && query.slice(0, -1).includes(";"))) {
    throw new Error("multiple statements are not allowed.");
  }
  query = query.replace(/;+\s*$/g, "").trim();

  if (!query.toLowerCase().startsWith("select")) {
    throw new Error("Only SELECT statements are allowed");
  }
  if (DENY_RE.test(query)) {
    throw new Error("DML/DDL detected. Only read-only queries are permitted.");
  }

  if (!HAS_LIMIT_TAIL_RE.test(query)) {
    query += " LIMIT 5";
  }
  return query;
}

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

export const agent = createAgent({
  model: "gpt-5.5",
  tools: [executeSql],
  systemPrompt: await getSystemPrompt(),
});
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

  console.log("✓ sql-agent-studio");
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
// :remove-end:
