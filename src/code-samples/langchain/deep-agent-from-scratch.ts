/** Build a data analysis agent from scratch using createAgent and Deep Agents middleware. */

// :snippet-start: deep-agent-from-scratch-minimal-js
import { createAgent } from "langchain";

let agent = createAgent({
  model: "openai:gpt-4.1",
  tools: [],
});
// :snippet-end:

// :snippet-start: deep-agent-from-scratch-sandbox-js
import { createFilesystemMiddleware, LangSmithSandbox } from "deepagents";
import { SandboxClient } from "langsmith/sandbox";

const client = new SandboxClient();
// :remove-start:
const SANDBOX_NAME = "langchain-docs";

function sandboxIdentifiers(sb: unknown): Array<string> {
  const record = sb as Record<string, unknown>;
  return [record.sandboxId, record.id, record.name, SANDBOX_NAME].filter(
    (value): value is string => typeof value === "string" && value.length > 0,
  );
}

async function namedSandboxes() {
  const sandboxes = await client.listSandboxes();
  return Array.from(sandboxes).filter(
    (sb) => (sb as { name?: string }).name === SANDBOX_NAME,
  );
}

async function deleteNamedSandboxes() {
  for (const existing of await namedSandboxes()) {
    for (const identifier of sandboxIdentifiers(existing)) {
      try {
        await client.deleteSandbox(identifier);
        break;
      } catch {
        // Try the next identifier form.
      }
    }
  }
}

for (let attempt = 0; attempt < 3; attempt += 1) {
  await deleteNamedSandboxes();
  if ((await namedSandboxes()).length === 0) {
    break;
  }
  await new Promise((resolve) => setTimeout(resolve, 1000));
}
// :remove-end:
const sandbox = await client.createSandbox({
  name: "langchain-docs",
  snapshotName: "docs-test-ci",
});
// :remove-start:
process.once("exit", () => {
  void deleteNamedSandboxes();
});
// :remove-end:
const backend = new LangSmithSandbox({ sandbox });

agent = createAgent({
  model: "openai:gpt-4.1",
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
      {
        role: "user",
        content:
          "Read /sales.csv and summarize total revenue by product in one sentence. Do not run shell commands.",
      },
    ],
  },
  { version: "v3", recursionLimit: 8 },
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
  model: "openai:gpt-4.1",
  tools: [],
  middleware: [
    createFilesystemMiddleware({ backend }),
    createSummarizationMiddleware({
      model: "openai:gpt-4.1",
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

let model = "openai:gpt-4.1";

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
  model: "openai:gpt-4.1",
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
try {
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
  console.log("✓ deep-agent-from-scratch sample completed");
} finally {
  await deleteNamedSandboxes();
}
// :remove-end:
