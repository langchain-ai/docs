import {
  createDeepAgent,
  type FilesystemPermission,
  CompositeBackend,
  StateBackend,
  StoreBackend,
} from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";

const model = "anthropic:claude-sonnet-4-6";
const backend = new StateBackend();

{
  // :snippet-start: permissions-basic-js
  const agent = createDeepAgent({
    model,
    backend,
    permissions: [
      {
        operations: ["write"],
        paths: ["/**"],
        mode: "deny",
      },
    ],
  });
  if (!agent) throw new Error("basic: agent not created");
  // :snippet-end:
}

{
  // :snippet-start: permissions-isolate-workspace-js
  const agent = createDeepAgent({
    model,
    backend,
    permissions: [
      {
        operations: ["read", "write"],
        paths: ["/workspace/**"],
        mode: "allow",
      },
      {
        operations: ["read", "write"],
        paths: ["/**"],
        mode: "deny",
      },
    ],
  });
  if (!agent) throw new Error("isolate-workspace: agent not created");
  // :snippet-end:
}

{
  // :snippet-start: permissions-protect-files-js
  const agent = createDeepAgent({
    model,
    backend,
    permissions: [
      {
        operations: ["read", "write"],
        paths: ["/workspace/.env", "/workspace/examples/**"],
        mode: "deny",
      },
      {
        operations: ["read", "write"],
        paths: ["/workspace/**"],
        mode: "allow",
      },
      {
        operations: ["read", "write"],
        paths: ["/**"],
        mode: "deny",
      },
    ],
  });
  if (!agent) throw new Error("protect-files: agent not created");
  // :snippet-end:
}

{
  // :snippet-start: permissions-read-only-memory-js
  const store = new InMemoryStore();
  const agent = createDeepAgent({
    model,
    backend: new CompositeBackend(new StateBackend(), {
      "/memories/": new StoreBackend({
        namespace: (rt) => [rt.serverInfo.user.identity],
      }),
      "/policies/": new StoreBackend({
        namespace: (rt) => [rt.context.orgId],
      }),
    }),
    permissions: [
      {
        operations: ["write"],
        paths: ["/memories/**", "/policies/**"],
        mode: "deny",
      },
    ],
    store,
  });
  if (!agent) throw new Error("read-only-memory: agent not created");
  // :snippet-end:
}

{
  // :snippet-start: permissions-deny-all-js
  const agent = createDeepAgent({
    model,
    backend,
    permissions: [
      {
        operations: ["read", "write"],
        paths: ["/**"],
        mode: "deny",
      },
    ],
  });
  if (!agent) throw new Error("deny-all: agent not created");
  // :snippet-end:
}

{
  // :snippet-start: permissions-rule-ordering-js
  const correctPermissions: FilesystemPermission[] = [
    { operations: ["read", "write"], paths: ["/workspace/.env"], mode: "deny" },
    {
      operations: ["read", "write"],
      paths: ["/workspace/**"],
      mode: "allow",
    },
    { operations: ["read", "write"], paths: ["/**"], mode: "deny" },
  ];

  const incorrectPermissions: FilesystemPermission[] = [
    {
      operations: ["read", "write"],
      paths: ["/workspace/**"],
      mode: "allow",
    },
    {
      operations: ["read", "write"],
      paths: ["/workspace/.env"],
      mode: "deny",
    },
    { operations: ["read", "write"], paths: ["/**"], mode: "deny" },
  ];
  // :snippet-end:
  const agentCorrect = createDeepAgent({
    model,
    backend,
    permissions: correctPermissions,
  });
  const agentIncorrect = createDeepAgent({
    model,
    backend,
    permissions: incorrectPermissions,
  });
  if (!agentCorrect || !agentIncorrect)
    throw new Error("rule-ordering: agents not created");
}

{
  // :snippet-start: permissions-subagent-js
  const agent = createDeepAgent({
    model,
    backend,
    permissions: [
      {
        operations: ["read", "write"],
        paths: ["/workspace/**"],
        mode: "allow",
      },
      { operations: ["read", "write"], paths: ["/**"], mode: "deny" },
    ],
    subagents: [
      {
        name: "auditor",
        description: "Read-only code reviewer",
        systemPrompt: "Review the code for issues.",
        permissions: [
          { operations: ["write"], paths: ["/**"], mode: "deny" },
          { operations: ["read"], paths: ["/workspace/**"], mode: "allow" },
          { operations: ["read"], paths: ["/**"], mode: "deny" },
        ],
      },
    ],
  });
  if (!agent) throw new Error("subagent: agent not created");
  // :snippet-end:
}

{
  // :snippet-start: permissions-composite-backend-js
  const sandbox = new StateBackend();
  const memoriesBackend = new StateBackend();
  const composite = new CompositeBackend(sandbox, {
    "/memories/": memoriesBackend,
  });
  const agent = createDeepAgent({
    model,
    backend: composite,
    permissions: [
      { operations: ["write"], paths: ["/memories/**"], mode: "deny" },
    ],
  });
  if (!agent) throw new Error("composite-backend: agent not created");
  // :snippet-end:
}

{
  // :snippet-start: permissions-composite-backend-invalid-js
  const sandbox = new StateBackend();
  const memoriesBackend = new StateBackend();
  const composite = new CompositeBackend(sandbox, {
    "/memories/": memoriesBackend,
  });

  createDeepAgent({
    model,
    backend: composite,
    permissions: [
      { operations: ["write"], paths: ["/workspace/**"], mode: "deny" },
    ],
  });

  createDeepAgent({
    model,
    backend: composite,
    permissions: [{ operations: ["read"], paths: ["/**"], mode: "deny" }],
  });
  // :snippet-end:
}
console.log("✓ All permissions examples verified");
