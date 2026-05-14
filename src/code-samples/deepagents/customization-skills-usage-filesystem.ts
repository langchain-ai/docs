import { copyFile, mkdir, mkdtemp } from "node:fs/promises";
import { dirname, join } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";

import { createCodeInterpreterMiddleware } from "@langchain/quickjs";
import { createDeepAgent, FilesystemBackend } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const __dirname = dirname(fileURLToPath(import.meta.url));

// :snippet-start: skills-usage-filesystem-js
const checkpointer = new MemorySaver();
const rootDir = await mkdtemp(join(tmpdir(), "deepagents-skills-"));
const backend = new FilesystemBackend({ rootDir, virtualMode: true });

const skillsDir = join(rootDir, "skills", "write-timestamp");
await mkdir(skillsDir, { recursive: true });
await copyFile(
  join(__dirname, "skills/write-timestamp/SKILL.md"),
  join(skillsDir, "SKILL.md"),
);

// KEEP MODEL
const agent = await createDeepAgent({
  model: "google_genai:gemini-3.1-pro-preview",
  backend,
  skills: [join(rootDir, "skills")],
  interruptOn: {
    read_file: true,
    write_file: true,
    delete_file: true,
  },
  checkpointer,
  middleware: [createCodeInterpreterMiddleware({ skillsBackend: backend })],
});

// Example invocation (requires LLM credentials):
// const config = { configurable: { thread_id: `thread-${Date.now()}` } };
// const result = await agent.invoke(
//   { messages: [{ role: "user", content: "what is langraph?" }] },
//   config,
// );
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
// :remove-end:
