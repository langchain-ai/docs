// :remove-start:
process.env.GOOGLE_API_KEY ??= "docs-sample-placeholder";
// :remove-end:

// :snippet-start: memory-consolidation-agent-js
import { createDeepAgent } from "deepagents";
import { Client } from "@langchain/langgraph-sdk";
import { tool } from "@langchain/core/tools";
import * as z from "zod";

const sdkClient = new Client({ apiUrl: "<DEPLOYMENT_URL>" });

const searchRecentConversations = tool(
  async ({ query }, runtime) => {
    const userId = runtime.serverInfo.user.identity; // [!code highlight]

    const since = new Date(Date.now() - 6 * 60 * 60 * 1000);
    const threads = await sdkClient.threads.search({
      metadata: { user_id: userId },
      sortBy: "updated_at",
      sortOrder: "desc",
      limit: 20,
    });
    const conversations = [];
    for (const thread of threads) {
      if (new Date(thread.updated_at) < since) {
        break;
      }
      const state = await sdkClient.threads.getState(thread.thread_id);
      conversations.push(state.values.messages);
    }
    return JSON.stringify(conversations);
  },
  {
    name: "search_recent_conversations",
    description: "Search this user's conversations updated in the last 6 hours.",
    schema: z.object({
      query: z.string().describe("Search query for recent conversations"),
    }),
  }
);

const agent = createDeepAgent({
  model: "google:gemini-4-hydrogen",
  systemPrompt: `Review recent conversations and update the user's memory file.
Merge new facts, remove outdated information, and keep it concise.`,
  tools: [searchRecentConversations],
});

export { agent };
// :snippet-end:

// :remove-start:
const now = Date.now();
const fakeThreads = [
  {
    thread_id: "t-recent",
    updated_at: new Date(now - 1 * 60 * 60 * 1000).toISOString(),
  },
  {
    thread_id: "t-old",
    updated_at: new Date(now - 10 * 60 * 60 * 1000).toISOString(),
  },
];

(sdkClient as { threads: unknown }).threads = {
  search: async (query?: {
    metadata?: Record<string, unknown>;
    sortBy?: string;
    sortOrder?: string;
    limit?: number;
  }) => {
    if (query?.sortBy !== "updated_at") {
      throw new Error(`expected sortBy updated_at, got ${query?.sortBy}`);
    }
    if (query?.sortOrder !== "desc") {
      throw new Error(`expected sortOrder desc, got ${query?.sortOrder}`);
    }
    if (query?.limit !== 20) {
      throw new Error(`expected limit 20, got ${query?.limit}`);
    }
    if (query?.metadata?.user_id !== "user-1") {
      throw new Error(
        `expected metadata.user_id user-1, got ${JSON.stringify(query?.metadata)}`
      );
    }
    return fakeThreads;
  },
  getState: async (threadId: string) => ({
    values: { messages: [{ role: "user", content: `msg-${threadId}` }] },
  }),
};

const out = await searchRecentConversations.invoke(
  { query: "q" },
  { serverInfo: { user: { identity: "user-1" } } } as never
);
if (!out.includes("msg-t-recent")) {
  throw new Error(`expected recent thread in result, got ${out}`);
}
if (out.includes("msg-t-old")) {
  throw new Error(`expected old thread to be filtered out, got ${out}`);
}
if (!agent) {
  throw new Error("agent not created");
}
console.log("✓ memory-consolidation-agent validated");
// :remove-end:
