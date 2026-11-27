// :remove-start:
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { FilesystemBackend } from "deepagents";

process.env.GOOGLE_API_KEY ??= "docs-sample-placeholder";
process.env.GEMINI_API_KEY ??= "docs-sample-placeholder";

const liveSandbox = process.env.DEEPAGENTS_LIVE_SANDBOX === "1";
const tmpRoot = mkdtempSync(
  join(tmpdir(), "deepagents-production-sandbox-sync-"),
);

class LocalSandbox {
  name = "local-test-sandbox";
}

class LocalSandboxClient {
  async createSandbox() {
    return new LocalSandbox();
  }

  async deleteSandbox(_name: string) {
    return;
  }
}
// :remove-end:

// :snippet-start: deepagents-production-sandbox-sync-js
import { createMiddleware } from "langchain";
import {
  createDeepAgent,
  CompositeBackend,
  LangSmithSandbox,
  StoreBackend,
} from "deepagents";
import { SandboxClient } from "langsmith/sandbox";

function safeFilename(key: string): string {
  const name = key.split("/").pop()!;
  if (name.includes("..") || /[*?]/.test(name)) {
    throw new Error(`Invalid key: ${key}`);
  }
  return name;
}

// Call the sandbox directly. CompositeBackend routes /skills/ and /memories/
// to StoreBackend, so uploadFiles on the composite would write back to the
// store instead of seeding the container.
const createSandboxSyncMiddleware = (sandbox: LangSmithSandbox) => {
  return createMiddleware({
    name: "SandboxSyncMiddleware",
    beforeAgent: async (state, runtime) => {
      // Upload skill scripts and memories into the sandbox
      const userId = runtime.serverInfo.user.identity; // [!code highlight]
      const store = runtime.store;
      const encoder = new TextEncoder();
      const files: [string, Uint8Array][] = [];
      for (const item of await store.search(["skills", userId])) {
        const name = safeFilename(item.key);
        files.push([`/skills/${name}`, encoder.encode(item.value.content)]);
      }
      for (const item of await store.search(["memories", userId])) {
        const name = safeFilename(item.key);
        files.push([`/memories/${name}`, encoder.encode(item.value.content)]);
      }
      if (files.length > 0) {
        await sandbox.uploadFiles(files);
      }
    },
    afterAgent: async (state, runtime) => {
      // Sync updated memories back to the store
      const userId = runtime.serverInfo.user.identity; // [!code highlight]
      const store = runtime.store;
      const items = await store.search(["memories", userId]);
      const results = await sandbox.downloadFiles(
        items.map((item) => `/memories/${item.key}`),
      );
      const decoder = new TextDecoder();
      for (const result of results) {
        if (result.content) {
          await store.put(
            ["memories", userId],
            result.path.split("/").pop()!,
            { content: decoder.decode(result.content) },
          );
        }
      }
    },
  });
};

// :remove-start:
const ClientCtor = liveSandbox ? SandboxClient : LocalSandboxClient;
const SandboxCtor = liveSandbox
  ? LangSmithSandbox
  : (function LocalLangSmithSandbox(_opts: { sandbox: LocalSandbox }) {
      return new FilesystemBackend({
        rootDir: tmpRoot,
        virtualMode: true,
      });
    } as unknown as typeof LangSmithSandbox);

const client = new ClientCtor();
const lsSandbox = await client.createSandbox();
const sandboxBackend = new (SandboxCtor as any)({
  sandbox: lsSandbox,
}) as LangSmithSandbox;
// :remove-end:
// :remove-start:
if (false) {
// :remove-end:
const client = new SandboxClient();
const lsSandbox = await client.createSandbox();
const sandboxBackend = new LangSmithSandbox({ sandbox: lsSandbox });
// :remove-start:
  void client;
  void lsSandbox;
  void sandboxBackend;
}
// :remove-end:

const backend = new CompositeBackend(sandboxBackend, {
  "/skills/": new StoreBackend({
    namespace: (rt) => ["skills", rt.serverInfo.user.identity], // [!code highlight]
  }),
  "/memories/": new StoreBackend({
    namespace: (rt) => ["memories", rt.serverInfo.user.identity], // [!code highlight]
  }),
});

export const agent = await createDeepAgent({
  model: "google:gemini-4-hydrogen",
  backend,
  middleware: [createSandboxSyncMiddleware(sandboxBackend)],
});
// :snippet-end:

// :remove-start:
import { InMemoryStore } from "@langchain/langgraph";

async function validateMiddleware() {
  const store = new InMemoryStore();
  const userId = "user-1";
  await store.put(["skills", userId], "skill.md", { content: "print(1)\n" });
  await store.put(["memories", userId], "note.md", { content: "hello\n" });

  const runtime = {
    store,
    serverInfo: { user: { identity: userId } },
  };

  const middleware = createSandboxSyncMiddleware(sandboxBackend);
  await middleware.beforeAgent!({}, runtime as any);

  const uploaded = await sandboxBackend.downloadFiles([
    "/skills/skill.md",
    "/memories/note.md",
  ]);
  if (uploaded.some((r) => !r.content)) {
    throw new Error(`expected sandbox files, got ${JSON.stringify(uploaded)}`);
  }

  await sandboxBackend.uploadFiles([
    ["/memories/note.md", new TextEncoder().encode("updated\n")],
  ]);
  await middleware.afterAgent!({}, runtime as any);

  const item = await store.get(["memories", userId], "note.md");
  if (!item || (item.value as { content: string }).content !== "updated\n") {
    throw new Error(`expected updated memory, got ${JSON.stringify(item)}`);
  }
}

async function main() {
  if (!agent) {
    throw new Error("expected agent");
  }
  try {
    await validateMiddleware();
    console.log("✓ deepagents-production-sandbox-sync-js validated");
  } finally {
    if (liveSandbox) {
      await client.deleteSandbox(lsSandbox.name);
    }
    rmSync(tmpRoot, { recursive: true, force: true });
  }
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
// :remove-end:
