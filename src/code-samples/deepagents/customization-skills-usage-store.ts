// :snippet-start: skills-usage-store-js
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";
import { createDeepAgent, StoreBackend, type FileData } from "deepagents";
import { InMemoryStore, MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();
const store = new InMemoryStore();
const backend = new StoreBackend();

function createFileData(content: string): FileData {
  const now = new Date().toISOString();
  return {
    content: content.split("\n"),
    created_at: now,
    modified_at: now,
  };
}

const skillUrl =
  "https://raw.githubusercontent.com/langchain-ai/deepagentsjs/refs/heads/main/examples/skills/langgraph-docs/SKILL.md";

const response = await fetch(skillUrl);
const skillContent = await response.text();
const fileData = createFileData(skillContent);

await store.put(["filesystem"], "/skills/langgraph-docs/SKILL.md", fileData);

// KEEP MODEL
const agent = await createDeepAgent({
  model: "google-genai:gemini-3.1-pro-preview",
  backend,
  store,
  checkpointer,
  // IMPORTANT: deepagents skill source paths are virtual (POSIX) paths relative to the backend root.
  skills: ["/skills/"],
  middleware: [createCodeInterpreterMiddleware({ skillsBackend: backend })],
});

const config = {
  recursionLimit: 50,
  configurable: { thread_id: `thread-${Date.now()}` },
};
const result = await agent.invoke(
  { messages: [{ role: "user", content: "what is langraph?" }] },
  config,
);
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
if (!result) throw new Error("result empty");
// :remove-end:
