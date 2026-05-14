// :snippet-start: customization-memory-store-js
import { createDeepAgent, StoreBackend, type FileData } from "deepagents";
import { InMemoryStore, MemorySaver } from "@langchain/langgraph";

const AGENTS_MD_URL =
  "https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/examples/text-to-sql-agent/AGENTS.md";

async function fetchText(url: string): Promise<string> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch ${url}: ${res.status} ${res.statusText}`);
  }
  return await res.text();
}

const agentsMd = await fetchText(AGENTS_MD_URL);

function createFileData(content: string): FileData {
  const now = new Date().toISOString();
  return {
    content,
    mimeType: "text/plain",
    created_at: now,
    modified_at: now,
  };
}

const store = new InMemoryStore();
const fileData = createFileData(agentsMd);
await store.put(["filesystem"], "/AGENTS.md", fileData);

const checkpointer = new MemorySaver();

const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  backend: new StoreBackend(),
  store: store,
  checkpointer: checkpointer,
  memory: ["/AGENTS.md"],
});

const result = await agent.invoke(
  {
    messages: [
      {
        role: "user",
        content: "Please tell me what's in your memory files.",
      },
    ],
  },
  { configurable: { thread_id: "12345" } },
);
// :snippet-end:

// :remove-start:
if (!result) throw new Error("No result returned");
// :remove-end:
