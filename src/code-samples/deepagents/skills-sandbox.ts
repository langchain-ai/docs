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
import { z } from "zod";

import { DaytonaSandbox } from "@langchain/daytona";

const SKILLS_ROOT = "/tmp/skills";
const DEMO_USER_ID = "demo-user";

function createFileData(content: string): FileData {
  const now = new Date().toISOString();
  return {
    content: content.split("\n"),
    created_at: now,
    modified_at: now,
  };
}

function safeStoreKey(key: string): string {
  // Store keys are absolute-ish paths inside a routed root (e.g. "/skill/dir/file").
  // Reject traversal and glob patterns before using them as sandbox paths.
  if (!key.startsWith("/") || key.includes("..") || /[*?]/.test(key)) {
    throw new Error(`Invalid key: ${key}`);
  }
  return key;
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

async function seedSkillStore(store: InMemoryStore, userId: string) {
  const moduleDir = resolve(fileURLToPath(new URL(".", import.meta.url)));
  const skillsDir = resolve(moduleDir, "skills");
  const filePaths = await walkFiles(skillsDir);
  for (const filePath of filePaths) {
    const rel = relative(skillsDir, filePath);
    // StoreBackend keys are paths *relative to the routed backend root*.
    // CompositeBackend strips the route prefix (`/tmp/skills/`) before delegating,
    // so store keys should look like "/<skillname>/SKILL.md".
    const key = `/${posix.normalize(rel.split("\\").join("/"))}`;
    const content = await readFile(filePath, "utf8");
    await store.put(["skills", userId], key, createFileData(content));
  }
}

const contextSchema = z.object({
  userId: z.string(),
});

function createSkillSandboxSyncMiddleware(sandbox: any) {
  const encoder = new TextEncoder();

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

      const userId =
        (runtime as any).serverInfo?.user?.identity ??
        (runtime as any).context?.userId ??
        DEMO_USER_ID;

      const files: Array<[string, Uint8Array]> = [];

      // Sync skills into the sandbox so scripts can be executed.
      for (const item of await store.search(["skills", userId])) {
        const key = safeStoreKey(String(item.key));
        const data = item.value as FileData;
        files.push([
          `${SKILLS_ROOT}${key}`,
          encoder.encode(data.content.join("\n")),
        ]);
      }

      if (files.length > 0) await sandbox.uploadFiles(files);

      return state;
    },
  });
}

async function main() {
  const store = new InMemoryStore();
  await seedSkillStore(store, DEMO_USER_ID);

  const sandbox = await DaytonaSandbox.create({
    language: "python",
    timeout: 300,
  });

  const backend = new CompositeBackend(sandbox, {
    [`${SKILLS_ROOT}/`]: new StoreBackend(
      { store: store as any, assistantId: undefined, state: {} } as any,
      { namespace: ["skills", DEMO_USER_ID] } as any,
    ),
  });

  try {
    const agent = await createDeepAgent({
      model: "anthropic:claude-sonnet-4-6",
      backend,
      skills: [`${SKILLS_ROOT}/`],
      store,
      contextSchema,
      middleware: [createSkillSandboxSyncMiddleware(sandbox)],
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
        context: { userId: DEMO_USER_ID },
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
