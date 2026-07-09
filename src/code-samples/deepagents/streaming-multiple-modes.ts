// :remove-start:
import { createDeepAgent } from "deepagents";
import { tool, type ToolRuntime } from "langchain";
import { z } from "zod";

const analyzeData = tool(
  async ({ topic }: { topic: string }, config: ToolRuntime) => {
    const writer = config.writer;
    writer?.({ status: "starting", topic, progress: 0 });
    await new Promise((r) => setTimeout(r, 500));
    writer?.({ status: "analyzing", progress: 50 });
    await new Promise((r) => setTimeout(r, 500));
    writer?.({ status: "complete", progress: 100 });
    return `Analysis of "${topic}": Customer sentiment is 85% positive.`;
  },
  {
    name: "analyze_data",
    description: "Run a data analysis on a given topic.",
    schema: z.object({ topic: z.string() }),
  },
);

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  systemPrompt:
    "You are a coordinator. For any analysis request, you MUST delegate " +
    "to the analyst subagent using the task tool. Never try to answer directly.",
  subagents: [
    {
      name: "analyst",
      description: "Performs data analysis with real-time progress tracking",
      systemPrompt:
        "You are a data analyst. You MUST call the analyze_data tool for every analysis request.",
      tools: [analyzeData],
    },
  ],
});
// :remove-end:

// :snippet-start: streaming-multiple-modes-js
// Skip internal middleware steps - only show meaningful node names
const INTERESTING_NODES = new Set(["model_request", "tools"]);

let lastSource = "";
let midLine = false; // true when we've written tokens without a trailing newline

for await (const [namespace, mode, data] of await agent.stream(
  {
    messages: [
      {
        role: "user",
        content: "Analyze the impact of remote work on team productivity",
      },
    ],
  },
  { streamMode: ["updates", "messages", "custom"], subgraphs: true },
)) {
  const isSubagent = namespace.some((s: string) => s.startsWith("tools:"));
  const source = isSubagent ? "subagent" : "main";

  if (mode === "updates") {
    for (const nodeName of Object.keys(data)) {
      if (!INTERESTING_NODES.has(nodeName)) continue;
      if (midLine) {
        process.stdout.write("\n");
        midLine = false;
      }
      console.log(`[${source}] step: ${nodeName}`);
    }
  } else if (mode === "messages") {
    const [message] = data;
    if (message.text) {
      // Print a header when the source changes
      if (source !== lastSource) {
        if (midLine) {
          process.stdout.write("\n");
          midLine = false;
        }
        process.stdout.write(`\n[${source}] `);
        lastSource = source;
      }
      process.stdout.write(message.text);
      midLine = true;
    }
  } else if (mode === "custom") {
    if (midLine) {
      process.stdout.write("\n");
      midLine = false;
    }
    console.log(`[${source}] custom event:`, data);
  }
}

process.stdout.write("\n");
// :snippet-end:

// :remove-start:
console.log("✓ streaming-multiple-modes validated");
// :remove-end:
