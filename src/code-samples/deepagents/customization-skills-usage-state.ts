import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { createCodeInterpreterMiddleware } from "@langchain/quickjs";
import { createDeepAgent, StateBackend, type FileData } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const __dirname = dirname(fileURLToPath(import.meta.url));

// :snippet-start: skills-usage-state-js
const checkpointer = new MemorySaver();
const backend = new StateBackend();

function createFileData(content: string): FileData {
  const now = new Date().toISOString();
  return {
    content: content.split("\n"),
    created_at: now,
    modified_at: now,
  };
}

const skillsFiles: Record<string, FileData> = {};
const skillPath = join(__dirname, "skills/write-timestamp/SKILL.md");
const skillContent = await readFile(skillPath, "utf-8");
skillsFiles["/skills/write-timestamp/SKILL.md"] = createFileData(skillContent);

// KEEP MODEL
const agent = await createDeepAgent({
  model: "google_genai:gemini-3.1-pro-preview",
  backend,
  checkpointer,
  skills: ["/skills/"],
  middleware: [createCodeInterpreterMiddleware({ skillsBackend: backend })],
});

// Example invocation (requires LLM credentials):
// const config = { configurable: { threadId: `thread-${Date.now()}` } };
// const result = await agent.invoke(
//   { messages: [{ role: "user", content: "what is langraph?" }], files: skillsFiles },
//   config,
// );
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
// :remove-end:
