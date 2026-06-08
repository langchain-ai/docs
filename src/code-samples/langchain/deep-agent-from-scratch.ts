/** Build a data analysis agent from scratch using createAgent and Deep Agents middleware. */

// :snippet-start: deep-agent-from-scratch-minimal-js
import { createAgent } from "langchain";

let agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [],
});
// :snippet-end:

// :snippet-start: deep-agent-from-scratch-sandbox-js
import { createFilesystemMiddleware, LangSmithSandbox } from "deepagents";
import { SandboxClient } from "langsmith/sandbox";

const client = new SandboxClient();
// :remove-start:
const snapshots = await client.listSnapshots({
  nameContains: "langchain-docs",
  limit: 100,
});
const langchainDocsSnapshots = Array.from(snapshots).filter(
  (snapshot) => snapshot.name === "langchain-docs" && snapshot.id,
);
for (const snapshot of langchainDocsSnapshots) {
  await client.deleteSnapshot(snapshot.id);
}
// :remove-end:
const sandbox = await client.createSandbox({ name: "langchain-docs" });
const backend = new LangSmithSandbox({ sandbox });

agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [],
  middleware: [createFilesystemMiddleware({ backend })],
});
// :snippet-end:

// :snippet-start: deep-agent-from-scratch-upload-js
const rows = [
  ["Date", "Product", "Units", "Revenue"],
  ["2025-08-01", "Widget A", "10", "250"],
  ["2025-08-02", "Widget B", "5", "125"],
  ["2025-08-03", "Widget A", "7", "175"],
  ["2025-08-04", "Widget C", "3", "90"],
];

const csv = rows.map((row) => row.join(",")).join("\n");
const encoder = new TextEncoder();
await backend.uploadFiles([["/sales.csv", encoder.encode(csv)]]);

const uploadStream = await agent.streamEvents(
  {
    messages: [
      { role: "user", content: "Analyze sales.csv. Summarize trends." },
    ],
  },
  { version: "v3", recursionLimit: 30 },
);

await Promise.all([
  (async () => {
    for await (const message of uploadStream.messages) {
      console.log(await message.text);
    }
  })(),
  uploadStream.output,
]);
// :snippet-end:

// :snippet-start: deep-agent-from-scratch-summarization-js
import { createSummarizationMiddleware } from "deepagents";

agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [],
  middleware: [
    createFilesystemMiddleware({ backend }),
    createSummarizationMiddleware({
      model: "anthropic:claude-sonnet-4-6",
      backend,
    }),
  ],
});
// :snippet-end:

// :snippet-start: deep-agent-from-scratch-skills-upload-js
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const skillsDir = resolve(
  fileURLToPath(new URL(".", import.meta.url)),
  "skills",
);
const skillFiles: Array<[string, Uint8Array]> = [];

function collectSkillFiles(dir: string): void {
  for (const entry of readdirSync(dir)) {
    const fullPath = join(dir, entry);
    if (statSync(fullPath).isDirectory()) {
      collectSkillFiles(fullPath);
    } else {
      const rel = relative(skillsDir, fullPath).replace(/\\/g, "/");
      skillFiles.push([`/skills/${rel}`, readFileSync(fullPath)]);
    }
  }
}

collectSkillFiles(skillsDir);
await backend.uploadFiles(skillFiles);
// :snippet-end:

// :snippet-start: deep-agent-from-scratch-skills-js
import { createSkillsMiddleware } from "deepagents";

let model = "anthropic:claude-sonnet-4-6";

agent = createAgent({
  model,
  tools: [],
  middleware: [
    createFilesystemMiddleware({ backend }),
    createSummarizationMiddleware({ model, backend }),
    createSkillsMiddleware({ backend, sources: ["/skills/"] }),
  ],
});
// :snippet-end:

// :snippet-start: deep-agent-from-scratch-subagent-js
import { todoListMiddleware } from "langchain";
import { createSubAgentMiddleware, type SubAgent } from "deepagents";

const visualizer: SubAgent = {
  name: "visualizer",
  description:
    "Generates charts and visualizations from data files in the sandbox.",
  systemPrompt:
    "You are a data visualization specialist. Write Python scripts using matplotlib and seaborn. Save all figures as PNG files.",
  tools: [],
  model: "anthropic:claude-sonnet-4-6",
};

agent = createAgent({
  model,
  tools: [],
  middleware: [
    createFilesystemMiddleware({ backend }),
    createSummarizationMiddleware({ model, backend }),
    createSkillsMiddleware({ backend, sources: ["/skills/"] }),
    todoListMiddleware(),
    createSubAgentMiddleware({
      defaultModel: model,
      defaultTools: [],
      subagents: [visualizer],
    }),
  ],
});
// :snippet-end:

// :remove-start:
const salesRead = await backend.read("/sales.csv");
if (salesRead.error) {
  throw new Error(salesRead.error);
}
const skillsRead = await backend.read("/skills/pandas-patterns/SKILL.md");
if (skillsRead.error) {
  throw new Error(skillsRead.error);
}
if (!agent) {
  throw new Error("expected agent");
}

const stream = await agent.streamEvents(
  {
    messages: [
      {
        role: "user",
        content:
          "Use read_file on /sales.csv only. Summarize total revenue by product in one short sentence. Do not use glob or list other directories.",
      },
    ],
  },
  { version: "v3", recursionLimit: 30 },
);

let sawMessage = false;
await Promise.all([
  (async () => {
    for await (const message of stream.messages) {
      sawMessage = true;
      console.log("[agent]", await message.text);
    }
  })(),
  stream.output,
]);
if (!sawMessage) {
  throw new Error("expected at least one streamed message");
}
console.log("✓ deep-agent-from-scratch sample completed");
// :remove-end:
