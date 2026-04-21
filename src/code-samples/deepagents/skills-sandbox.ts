// :snippet-start: skills-sandbox-js
import { readFile, readdir } from "node:fs/promises";
import { join, posix, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { createMiddleware } from "langchain";
import {
  CompositeBackend,
  createDeepAgent,
  type FileData,
  StoreBackend,
} from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";

import { DaytonaSandbox } from "@langchain/daytona";

/** Identical skill bundles for every user: one shared store namespace. */
const SKILLS_SHARED_NAMESPACE = ["skills", "builtin"] as const;

function createFileData(content: string): FileData {
  const now = new Date().toISOString();
  return {
    content: content.split("\n"),
    created_at: now,
    modified_at: now,
  };
}

function normalizeSkillsStoreKey(key: string): string {
  const k = String(key);
  if (k.includes("..") || /[*?]/.test(k)) {
    throw new Error(`Invalid key: ${key}`);
  }
  return k.startsWith("/") ? k : `/${k}`;
}

async function walkFiles(dir: string): Promise<string[]> {
  const entries = await readdir(dir, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await walkFiles(fullPath)));
    } else if (entry.isFile()) {
      files.push(fullPath);
    }
  }
  return files.sort((a, b) => a.localeCompare(b));
}

/** Load canonical skill files from disk into the shared store namespace (run once at deploy).
 *  You can retrieve skills from any source (local filesystem, remote URL, etc.).
 */
async function seedSkillStore(store: InMemoryStore) {
  const moduleDir = resolve(fileURLToPath(new URL(".", import.meta.url)));
  const skillsDir = resolve(moduleDir, "skills");
  const filePaths = await walkFiles(skillsDir);
  for (const filePath of filePaths) {
    const rel = relative(skillsDir, filePath);
    // StoreBackend keys are paths *relative to the routed backend root*.
    // CompositeBackend strips the route prefix (`/skills/`) before delegating,
    // so store keys should look like "/<skillname>/SKILL.md".
    const key = `/${posix.normalize(rel.split("\\").join("/"))}`;
    const content = await readFile(filePath, "utf8");
    await store.put([...SKILLS_SHARED_NAMESPACE], key, createFileData(content));
  }
}

/** Copy shared skill files from the store into the sandbox before each agent run. */
function createSkillSandboxSyncMiddleware(backend: CompositeBackend) {
  return createMiddleware({
    name: "SkillSandboxSyncMiddleware",
    beforeAgent: async (state, runtime) => {
      const store = (runtime as any).store;
      if (!store) {
        throw new Error(
          "Store is required for syncing skills into the sandbox. " +
            "Pass `store` to createDeepAgent and ensure your runtime provides it.",
        );
      }

      const encoder = new TextEncoder();
      const files: Array<[string, Uint8Array]> = [];

      for (const item of await store.search([...SKILLS_SHARED_NAMESPACE])) {
        const normalized = normalizeSkillsStoreKey(String(item.key));
        const data = item.value as FileData;
        // CompositeBackend routes paths and batches uploads to the right backend.
        files.push([
          `/skills${normalized}`,
          encoder.encode(data.content.join("\n")),
        ]);
      }

      if (files.length > 0) await backend.uploadFiles(files);

      return state;
    },
  });
}

async function main() {
  const store = new InMemoryStore();
  await seedSkillStore(store);

  const sandbox = await DaytonaSandbox.create({
    language: "python",
    timeout: 300,
  });

  const backend = new CompositeBackend(sandbox, {
    "/skills/": new StoreBackend({
      store,
      namespace: () => [...SKILLS_SHARED_NAMESPACE],
    } as any),
  });

  try {
    const agent = await createDeepAgent({
      model: "anthropic:claude-sonnet-4-6",
      backend,
      skills: ["/skills/"],
      store,
      middleware: [createSkillSandboxSyncMiddleware(backend)],
    });

    // :remove-start:
    const result = await agent.invoke(
      {
        messages: [
          {
            role: "user",
            content:
              "Use the write-timestamp skill to write the current date and time to a file, then tell me what you wrote.",
          },
        ],
      },
      {
        configurable: { thread_id: "skills-sandbox-demo" },
      },
    );

    const messages = result.messages ?? [];
    if (messages.length > 0) {
      const last = messages[messages.length - 1];
      console.log(
        typeof last.content === "string" ? last.content : String(last.content),
      );
    }
    // :remove-end:
  } finally {
    await sandbox.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
// :snippet-end:
