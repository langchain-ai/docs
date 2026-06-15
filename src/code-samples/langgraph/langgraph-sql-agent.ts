/** Build a custom SQL agent with LangGraph. */

// :snippet-start: langgraph-sql-agent-download-chinook-js
import fs from "node:fs/promises";
import path from "node:path";

const url =
  "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db";
const localPath = path.resolve("Chinook.db");

async function resolveDbPath() {
  const exists = await fs
    .access(localPath)
    .then(() => true)
    .catch(() => false);
  if (exists) {
    console.log(`${localPath} already exists, skipping download.`);
    return localPath;
  }
  const resp = await fetch(url);
  if (!resp.ok)
    throw new Error(`Failed to download DB. Status code: ${resp.status}`);
  const buf = Buffer.from(await resp.arrayBuffer());
  await fs.writeFile(localPath, buf);
  console.log(`File downloaded and saved as ${localPath}`);
  return localPath;
}
// :snippet-end:

// :snippet-start: langgraph-sql-agent-explore-database-js
import sqlite3 from "sqlite3";

const dialect = "sqlite";

async function runQuery(query: string, params: unknown[] = []): Promise<any[]> {
  const dbPath = await resolveDbPath();
  const db = new sqlite3.Database(dbPath);
  return new Promise((resolve, reject) => {
    db.all(query, params, (err, rows) => {
      db.close();
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

const tableRows = await runQuery(
  "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';",
);
const tableNames = tableRows.map((row) => String(row.name));
console.log(`Dialect: ${dialect}`);
console.log(`Available tables: ${tableNames.join(", ")}`);
const sampleResults = await runQuery("SELECT * FROM Artist LIMIT 5;");
console.log(`Sample output: ${JSON.stringify(sampleResults)}`);
// :snippet-end:

// :remove-start:
import { ChatOpenAI } from "@langchain/openai";

const model = process.env.OPENAI_API_KEY
  ? new ChatOpenAI({ model: "gpt-5.5" })
  : null;
// :remove-end:

// :snippet-start: langgraph-sql-agent-tools-js
import { tool } from "langchain";
import * as z from "zod";

async function getTableNames() {
  const rows = await runQuery(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';",
  );
  return rows.map((row) => String(row.name));
}

function quoteSqliteIdentifier(identifier: string) {
  return `"${identifier.replaceAll('"', '""')}"`;
}

const listTablesTool = tool(
  async () => {
    const tableNames = await getTableNames();
    return tableNames.join(", ");
  },
  {
    name: "sql_db_list_tables",
    description:
      "Input is an empty string, output is a comma-separated list of tables in the database.",
    schema: z.object({}),
  },
);

const getSchemaTool = tool(
  async ({ table_names }) => {
    const validTables = new Set(await getTableNames());
    const results: string[] = [];
    for (const table of table_names.split(",").map((t) => t.trim())) {
      if (!validTables.has(table)) {
        results.push(`Error: table_names {'${table}'} not found in database`);
        continue;
      }
      const schemaRows = await runQuery(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?;",
        [table],
      );
      const schema = schemaRows[0]?.sql;
      if (schema) {
        results.push(String(schema));
        try {
          const rows = await runQuery(
            `SELECT * FROM ${quoteSqliteIdentifier(table)} LIMIT 3;`,
          );
          if (rows.length > 0) {
            const colNames = Object.keys(rows[0]);
            results.push(
              `/*\n3 rows from ${table} table:\n${colNames.join("\t")}\n` +
                rows
                  .map((row) =>
                    colNames.map((col) => String(row[col])).join("\t"),
                  )
                  .join("\n") +
                "\n*/",
            );
          }
        } catch (e) {
          results.push(`Error fetching sample rows: ${e}`);
        }
      }
    }
    return results.join("\n\n");
  },
  {
    name: "sql_db_schema",
    description:
      "Input to this tool is a comma-separated list of tables, output is the schema and sample rows for those tables. Be sure that the tables actually exist by calling sql_db_list_tables first! Example Input: table1, table2, table3",
    schema: z.object({
      table_names: z.string().describe("Comma-separated list of table names"),
    }),
  },
);

const queryTool = tool(
  async ({ query }) => {
    try {
      const result = await runQuery(query);
      return JSON.stringify(result);
    } catch (error) {
      return `Error: ${error instanceof Error ? error.message : String(error)}`;
    }
  },
  {
    name: "sql_db_query",
    description:
      "Input to this tool is a detailed and correct SQL query, output is a result from the database. If the query is not correct, an error message will be returned. If an error is returned, rewrite the query, check the query, and try again.",
    schema: z.object({
      query: z.string().describe("SQL query to execute"),
    }),
  },
);

const tools = [listTablesTool, getSchemaTool, queryTool];

for (const toolItem of tools) {
  console.log(`${toolItem.name}: ${toolItem.description}\n`);
}
// :snippet-end:

// :snippet-start: langgraph-sql-agent-define-steps-js
import {
  AIMessage,
  HumanMessage,
  SystemMessage,
  ToolMessage,
} from "@langchain/core/messages";
import { ToolNode } from "@langchain/langgraph/prebuilt";
import {
  END,
  GraphNode,
  MessagesValue,
  START,
  StateGraph,
  StateSchema,
} from "@langchain/langgraph";

// Create tool nodes for schema and query execution
const getSchemaNode = new ToolNode([getSchemaTool]);
const runQueryNode = new ToolNode([queryTool]);

// Define state schema
const MessagesState = new StateSchema({
  messages: MessagesValue,
});

// Example: create a predetermined tool call
const listTables: GraphNode<typeof MessagesState> = async (state) => {
  const toolCall = {
    name: "sql_db_list_tables",
    args: {},
    id: "abc123",
    type: "tool_call" as const,
  };
  const toolCallMessage = new AIMessage({
    content: "",
    tool_calls: [toolCall],
  });

  const toolMessage = await listTablesTool.invoke({});
  const response = new AIMessage(`Available tables: ${toolMessage}`);

  return {
    messages: [
      toolCallMessage,
      new ToolMessage({ content: toolMessage, tool_call_id: "abc123" }),
      response,
    ],
  };
};

// Example: force a model to create a tool call
const callGetSchema: GraphNode<typeof MessagesState> = async (state) => {
  const llmWithTools = model!.bindTools([getSchemaTool], {
    tool_choice: "any",
  });
  const response = await llmWithTools.invoke(state.messages);

  return { messages: [response] };
};

const topK = 5;

const generateQuerySystemPrompt = `
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct ${dialect}
query to run, then look at the results of the query and return the answer. Unless
the user specifies a specific number of examples they wish to obtain, always limit
your query to at most ${topK} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
`;

const generateQuery: GraphNode<typeof MessagesState> = async (state) => {
  const systemMessage = new SystemMessage(generateQuerySystemPrompt);
  // We do not force a tool call here, to allow the model to
  // respond naturally when it obtains the solution.
  const llmWithTools = model!.bindTools([queryTool]);
  const response = await llmWithTools.invoke([
    systemMessage,
    ...state.messages,
  ]);

  return { messages: [response] };
};

const checkQuerySystemPrompt = `
You are a SQL expert with a strong attention to detail.
Double check the ${dialect} query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

If there are any of the above mistakes, rewrite the query. If there are no mistakes,
just reproduce the original query.

You will call the appropriate tool to execute the query after running this check.
`;

const checkQuery: GraphNode<typeof MessagesState> = async (state) => {
  const systemMessage = new SystemMessage(checkQuerySystemPrompt);

  // Generate an artificial user message to check
  const lastMessage = state.messages[state.messages.length - 1];
  if (!lastMessage.tool_calls || lastMessage.tool_calls.length === 0) {
    throw new Error("No tool calls found in the last message");
  }
  const toolCall = lastMessage.tool_calls[0];
  const userMessage = new HumanMessage(toolCall.args.query);
  const llmWithTools = model!.bindTools([queryTool], {
    tool_choice: "any",
  });
  const response = await llmWithTools.invoke([systemMessage, userMessage]);
  // Preserve the original message ID
  response.id = lastMessage.id;

  return { messages: [response] };
};
// :snippet-end:

// :snippet-start: langgraph-sql-agent-assemble-agent-js
import { ConditionalEdgeRouter } from "@langchain/langgraph";

const shouldContinue: ConditionalEdgeRouter<
  typeof MessagesState,
  "check_query"
> = (state) => {
  const messages = state.messages;
  const lastMessage = messages[messages.length - 1];
  if (!lastMessage.tool_calls || lastMessage.tool_calls.length === 0) {
    return END;
  } else {
    return "check_query";
  }
};

const builder = new StateGraph(MessagesState)
  .addNode("list_tables", listTables)
  .addNode("call_get_schema", callGetSchema)
  .addNode("get_schema", getSchemaNode)
  .addNode("generate_query", generateQuery)
  .addNode("check_query", checkQuery)
  .addNode("run_query", runQueryNode)
  .addEdge(START, "list_tables")
  .addEdge("list_tables", "call_get_schema")
  .addEdge("call_get_schema", "get_schema")
  .addEdge("get_schema", "generate_query")
  .addConditionalEdges("generate_query", shouldContinue)
  .addEdge("check_query", "run_query")
  .addEdge("run_query", "generate_query");

const agent = builder.compile();
// :snippet-end:

// :snippet-start: langgraph-sql-agent-visualize-graph-js
import * as fs from "node:fs/promises";

const drawableGraph = await agent.getGraphAsync();
const image = await drawableGraph.drawMermaidPng();
const imageBuffer = new Uint8Array(await image.arrayBuffer());

await fs.writeFile("graph.png", imageBuffer);
// :snippet-end:

// :snippet-start: langgraph-sql-agent-hitl-interrupt-js
import { RunnableConfig } from "@langchain/core/runnables";
import { interrupt } from "@langchain/langgraph";

const queryToolWithInterrupt = tool(
  async (input, config: RunnableConfig) => {
    const request = {
      action: queryTool.name,
      args: input,
      description: "Please review the tool call",
    };
    const response = interrupt([request]); // [!code highlight]
    // approve the tool call
    if (response.type === "accept") {
      const toolResponse = await queryTool.invoke(input, config);
      return toolResponse;
    }
    // update tool call args
    else if (response.type === "edit") {
      const editedInput = response.args.args;
      const toolResponse = await queryTool.invoke(editedInput, config);
      return toolResponse;
    }
    // respond to the LLM with user feedback
    else if (response.type === "response") {
      const userFeedback = response.args;
      return userFeedback;
    } else {
      throw new Error(`Unsupported interrupt response type: ${response.type}`);
    }
  },
  {
    name: queryTool.name,
    description: queryTool.description,
    schema: queryTool.schema,
  },
);
// :snippet-end:

const runQueryNodeWithInterrupt = new ToolNode([queryToolWithInterrupt]);

// :snippet-start: langgraph-sql-agent-hitl-assemble-js
import { Command, MemorySaver } from "@langchain/langgraph";

const shouldContinueWithHuman: ConditionalEdgeRouter<
  typeof MessagesState,
  "run_query"
> = (state) => {
  const messages = state.messages;
  const lastMessage = messages[messages.length - 1];
  if (!lastMessage.tool_calls || lastMessage.tool_calls.length === 0) {
    return END;
  } else {
    return "run_query";
  }
};

const builderWithHuman = new StateGraph(MessagesState)
  .addNode("list_tables", listTables)
  .addNode("call_get_schema", callGetSchema)
  .addNode("get_schema", getSchemaNode)
  .addNode("generate_query", generateQuery)
  .addNode("run_query", runQueryNodeWithInterrupt)
  .addEdge(START, "list_tables")
  .addEdge("list_tables", "call_get_schema")
  .addEdge("call_get_schema", "get_schema")
  .addEdge("get_schema", "generate_query")
  .addConditionalEdges("generate_query", shouldContinueWithHuman)
  .addEdge("run_query", "generate_query");

const checkpointer = new MemorySaver(); // [!code highlight]
const agentWithHuman = builderWithHuman.compile({ checkpointer }); // [!code highlight]
// :snippet-end:

// :remove-start:
async function main() {
  const dbPath = await resolveDbPath();
  const stat = await fs.stat(dbPath);
  if (stat.size <= 0) {
    throw new Error("Chinook.db is empty");
  }

  const tables = await listTablesTool.invoke({});
  if (!tables.includes("Artist")) {
    throw new Error(`Expected Artist in tables, got: ${tables}`);
  }

  const schema = await getSchemaTool.invoke({ table_names: "Artist" });
  if (!schema.includes("CREATE TABLE")) {
    throw new Error("Expected CREATE TABLE in schema output");
  }

  const queryResult = await queryTool.invoke({
    query: "SELECT COUNT(*) AS count FROM Artist",
  });
  if (queryResult.startsWith("Error:")) {
    throw new Error(`Unexpected query error: ${queryResult}`);
  }

  const listTablesResult = await listTables({ messages: [] });
  if (listTablesResult.messages.length !== 3) {
    throw new Error("Expected three messages from listTables node");
  }

  const noToolState = {
    messages: [new AIMessage("done")],
  };
  if (shouldContinue(noToolState) !== END) {
    throw new Error("Expected END when no tool calls are present");
  }

  const toolCallState = {
    messages: [
      new AIMessage({
        content: "",
        tool_calls: [
          {
            name: "sql_db_query",
            args: { query: "SELECT 1" },
            id: "1",
          },
        ],
      }),
    ],
  };
  if (shouldContinue(toolCallState) !== "check_query") {
    throw new Error("Expected check_query route when tool calls are present");
  }

  const graph = await agent.getGraphAsync();
  const png = await graph.drawMermaidPng();
  const pngBuffer = new Uint8Array(await png.arrayBuffer());
  if (pngBuffer.length === 0) {
    throw new Error("Expected non-empty graph PNG");
  }

  if (model) {
    // :snippet-start: langgraph-sql-agent-stream-agent-js
    const question = "Which genre on average has the longest tracks?";

    const stream = await agent.stream(
      { messages: [{ role: "user", content: question }] },
      { streamMode: "values" },
    );

    for await (const step of stream) {
      if (step.messages && step.messages.length > 0) {
        const lastMessage = step.messages[step.messages.length - 1];
        console.log(lastMessage.toFormattedString());
      }
    }
    // :snippet-end:

    const config = { configurable: { thread_id: "1" } };

    // :snippet-start: langgraph-sql-agent-hitl-stream-js
    const hitlQuestion = "Which genre on average has the longest tracks?";

    const hitlStream = await agentWithHuman.stream(
      { messages: [{ role: "user", content: hitlQuestion }] },
      { ...config, streamMode: "values" },
    );

    for await (const step of hitlStream) {
      if (step.messages && step.messages.length > 0) {
        const lastMessage = step.messages[step.messages.length - 1];
        console.log(lastMessage.toFormattedString());
      }
    }

    // Check for interrupts
    const state = await agentWithHuman.getState(config);
    if (state.next.length > 0) {
      console.log("\nINTERRUPTED:");
      console.log(JSON.stringify(state.tasks[0].interrupts[0], null, 2));
    }
    // :snippet-end:

    // :snippet-start: langgraph-sql-agent-hitl-resume-js
    const resumeStream = await agentWithHuman.stream(
      new Command({ resume: { type: "accept" } }),
      // new Command({ resume: { type: "edit", args: { query: "..." } } }),
      { ...config, streamMode: "values" },
    );

    for await (const step of resumeStream) {
      if (step.messages && step.messages.length > 0) {
        const lastMessage = step.messages[step.messages.length - 1];
        console.log(lastMessage.toFormattedString());
      }
    }
    // :snippet-end:
  }

  console.log("✓ langgraph-sql-agent");
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
// :remove-end:
