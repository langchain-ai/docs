// :remove-start:
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
// :remove-end:
// :snippet-start: skills-usage-filesystem-js
import { createDeepAgent, FilesystemBackend } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const skillUrl =
  "https://raw.githubusercontent.com/langchain-ai/deepagentsjs/refs/heads/main/examples/skills/langgraph-docs/SKILL.md";
const response = await fetch(skillUrl);
const skillContent = await response.text();

let backend = new FilesystemBackend({
  rootDir: process.cwd(),
  virtualMode: true,
});
// :remove-start:
backend = new FilesystemBackend({
  rootDir: mkdtempSync(join(tmpdir(), "deepagents-skills-")),
  virtualMode: true,
});
// :remove-end:
await backend.uploadFiles([
  ["/skills/langgraph-docs/SKILL.md", new TextEncoder().encode(skillContent)],
]);

// KEEP MODEL
const agent = await createDeepAgent({
  model: "google-genai:gemini-3.1-pro-preview",
  backend,
  // IMPORTANT: deepagents skill source paths are virtual (POSIX) paths relative to the backend root.
  skills: ["/skills/"],
  interruptOn: {
    read_file: true,
    write_file: true,
    delete_file: true,
  },
  checkpointer, // Required for filesystem operations!
});

const config = { configurable: { thread_id: `thread-${Date.now()}` } };
const result = await agent.invoke(
  { messages: [{ role: "user", content: "what is langraph?" }] },
  config,
);
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
if (!result) throw new Error("result empty");
// :remove-end:
