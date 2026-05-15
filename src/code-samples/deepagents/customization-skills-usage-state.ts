import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// :snippet-start: skills-usage-state-js
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";
import { createDeepAgent, StateBackend, type FileData } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();
const backend = new StateBackend();

// :remove-start:
const __dirname = dirname(fileURLToPath(import.meta.url));
// :remove-end:
function createFileData(content: string): FileData {
  const now = new Date().toISOString();
  return {
    content: content.split("\n"),
    created_at: now,
    modified_at: now,
  };
}

const skillsFiles: Record<string, FileData> = {};
const skillUrl =
  "https://raw.githubusercontent.com/langchain-ai/deepagentsjs/refs/heads/main/examples/skills/langgraph-docs/SKILL.md";
const response = await fetch(skillUrl);
const skillContent = await response.text();

skillsFiles["/skills/langgraph-docs/SKILL.md"] = createFileData(skillContent);

// KEEP MODEL
const agent = await createDeepAgent({
  model: "google-genai:gemini-3.1-pro-preview",
  backend,
  checkpointer, // Required !
  // IMPORTANT: deepagents skill source paths are virtual (POSIX) paths relative to the backend root.
  skills: ["/skills/"],
  middleware: [createCodeInterpreterMiddleware({ skillsBackend: backend })],
});

const config = { configurable: { thread_id: `thread-${Date.now()}` } };
const result = await agent.invoke(
  {
    messages: [{ role: "user", content: "what is langraph?" }],
    files: skillsFiles,
  },
  config,
);
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
if (!result) throw new Error("result not created");
// :remove-end:
