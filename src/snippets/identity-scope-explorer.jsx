"use client";

import { useState } from "react";

export const IdentityScopeExplorer = () => {
  const [scope, setScope] = useState({
    threads: "user",
    memory: "user",
    credentials: "user",
  });
  const [lang, setLang] = useState("ts");

  const threadScopes = ["user", "conversation", "organization"];
  const memoryScopes = ["user", "organization", "agent", "none"];
  const credentialScopes = ["user", "agent", "none", "custom"];

  const scopeAxes = {
    user: { threads: "user", memory: "user", credentials: "user" },
    organization: {
      threads: "user",
      memory: "organization",
      credentials: "none",
    },
    agent: { threads: "user", memory: "agent", credentials: "agent" },
    none: { threads: "user", memory: "none", credentials: "none" },
  };

  const presets = [
    {
      id: "user",
      label: "Private assistant",
      description: "Each caller gets private threads, memory, and credentials.",
      scope: scopeAxes.user,
    },
    {
      id: "organization",
      label: "Multi-tenant SaaS",
      description: "Private threads; memory shared inside each customer org.",
      scope: scopeAxes.organization,
    },
    {
      id: "channel",
      label: "Shared channel bot",
      description:
        "One channel conversation, one thread; keep per-caller memory.",
      scope: {
        threads: "conversation",
        memory: "user",
        credentials: "agent",
      },
    },
    {
      id: "agent",
      label: "Service agent",
      description:
        "Shared deployment memory and vault. Matches bare defineIdentity().",
      scope: scopeAxes.agent,
    },
  ];

  const threadBehavior = {
    user: "Only the signed-in caller can open or resume their threads. Alice cannot see or continue Bob's conversations.",
    conversation:
      "Everyone in the same upstream channel conversation (for example a Slack thread) shares one agent thread. Callers without a channel id, such as a browser session, fall back to user-owned threads.",
    organization:
      "Anyone in the same organization can open or resume those threads. Every request must present an organization id.",
  };

  const memoryBehavior = {
    user: "Durable Context Hub memory remounts as memories/<userId> (or memories/<organizationId>/<userId> when organizations are required). Each caller gets a private slice.",
    organization:
      "Memory remounts as memories/<organizationId>. Callers in the same org share durable notes; other orgs are unreachable. Every request must present an organization id.",
    agent: "Memory remounts as memories/agent. The whole deployment shares one slice.",
    none: "/memories/user is not mounted, and hot memory is not injected into the prompt.",
  };

  const credentialBehavior = {
    user: "Downstream tool calls can act as the signed-in user. Per-caller Connect-with-X routes mount when a credential chain reads user tokens.",
    agent:
      "Downstream calls use the shared deployment vault (mda connect / Settings → Integrations), not each caller's personal token.",
    none: "No managed credential owner. Connect is not inferred from memory scope.",
    custom:
      "You supply a credentials resolver or endpoint. Tools call runtime.credentials.for(target) to fetch headers for each platform.",
  };

  const scopesEqual = (a, b) =>
    a.threads === b.threads &&
    a.memory === b.memory &&
    a.credentials === b.credentials;

  const activePreset = presets.find((preset) => scopesEqual(scope, preset.scope));
  const namedScope = Object.keys(scopeAxes).find((name) =>
    scopesEqual(scope, scopeAxes[name])
  );
  const needsOrg = [scope.threads, scope.memory, scope.credentials].includes(
    "organization"
  );
  const needsExplicitOrg = needsOrg && !namedScope;

  const isCustomCredentials = scope.credentials === "custom";

  // When credentials are custom, the resolver implies custom mode — omit the
  // credentials axis from scope and show a demo resolve function instead.
  const formatScopeObject = isCustomCredentials
    ? lang === "python"
      ? `{\n        "threads": "${scope.threads}",\n        "memory": "${scope.memory}",\n    }`
      : `{\n    threads: "${scope.threads}",\n    memory: "${scope.memory}",\n  }`
    : lang === "python"
      ? `{\n        "threads": "${scope.threads}",\n        "memory": "${scope.memory}",\n        "credentials": "${scope.credentials}",\n    }`
      : `{\n    threads: "${scope.threads}",\n    memory: "${scope.memory}",\n    credentials: "${scope.credentials}",\n  }`;

  const pythonCredentialsBlock = `credentials={
        "github": {
            "resolve": resolve_github,
        },
    },`;

  const tsCredentialsBlock = `credentials: {
    github: {
      async resolve({ identity }) {
        const credential = await getAccessToken(identity.user.id);
        if (!credential) {
          throw new Error("Connect the provider before using its tools.");
        }
        return {
          headers: { Authorization: \`Bearer \${credential.token}\` },
          expiresAt: credential.expiresAt.toISOString(),
        };
      },
    },
  },`;

  let code;
  if (lang === "python") {
    if (isCustomCredentials) {
      const orgLine = needsExplicitOrg ? '\n    organization="required",' : "";
      code = `from managed_deepagents import define_identity

# Application code: look up and refresh the caller's grant.
def resolve_github(args):
    identity = args["identity"]
    credential = get_access_token(identity["user"]["id"])
    if not credential:
        raise ValueError("Connect the provider before using its tools.")
    return {
        "headers": {"Authorization": f"Bearer {credential['token']}"},
        "expires_at": credential["expires_at"],
    }

identity = define_identity(
    scope=${formatScopeObject},${orgLine}
    ${pythonCredentialsBlock}
)`;
    } else if (namedScope === "agent") {
      code = `from managed_deepagents import define_identity\n\nidentity = define_identity()\n# threads=user, memory=agent, credentials=agent`;
    } else if (namedScope) {
      code = `from managed_deepagents import define_identity\n\nidentity = define_identity(scope="${namedScope}")`;
    } else {
      const orgLine = needsExplicitOrg ? '\n    organization="required",' : "";
      code = `from managed_deepagents import define_identity\n\nidentity = define_identity(\n    scope=${formatScopeObject},${orgLine}\n)`;
    }
  } else if (isCustomCredentials) {
    const orgLine = needsExplicitOrg ? `\n  organization: "required",` : "";
    code = `import { defineIdentity } from "managed-deepagents";
import { getAccessToken } from "./credentials.js";

export const identity = defineIdentity({
  scope: ${formatScopeObject},${orgLine}
  ${tsCredentialsBlock}
});`;
  } else if (namedScope === "agent") {
    code = `import { defineIdentity } from "managed-deepagents";\n\nexport const identity = defineIdentity();\n// threads: user, memory: agent, credentials: agent`;
  } else if (namedScope) {
    code = `import { defineIdentity } from "managed-deepagents";\n\nexport const identity = defineIdentity({ scope: "${namedScope}" });`;
  } else {
    const orgLine = needsExplicitOrg ? `\n  organization: "required",` : "";
    code = `import { defineIdentity } from "managed-deepagents";\n\nexport const identity = defineIdentity({\n  scope: ${formatScopeObject},${orgLine}\n});`;
  }

  const updateAxis = (axis, value) => {
    setScope((current) => ({ ...current, [axis]: value }));
  };

  const axisSelect = (label, axis, options) => (
    <label className="flex flex-col gap-1.5 text-sm" key={axis}>
      <span className="font-medium text-gray-900 dark:text-gray-100">
        {label}
      </span>
      <select
        className="rounded-md border border-gray-300 bg-white px-2.5 py-1.5 text-sm text-gray-900 dark:border-gray-700 dark:bg-gray-950 dark:text-gray-100"
        onChange={(event) => updateAxis(axis, event.target.value)}
        value={scope[axis]}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );

  return (
    <div className="not-prose my-6 space-y-4 rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-900/40">
      <div>
        <div className="text-sm font-semibold text-gray-900 dark:text-gray-100">
          Explore identity scope
        </div>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
          Pick a product preset or override each axis to see who can access
          threads, how memory remounts, and whose credentials tools use.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {presets.map((preset) => {
          const selected = activePreset?.id === preset.id;
          return (
            <button
              className={
                selected
                  ? "rounded-full border border-blue-600 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-800 dark:border-blue-400 dark:bg-blue-950 dark:text-blue-100"
                  : "rounded-full border border-gray-300 bg-white px-3 py-1 text-xs font-medium text-gray-700 hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-950 dark:text-gray-200 dark:hover:bg-gray-800"
              }
              key={preset.id}
              onClick={() => setScope(preset.scope)}
              title={preset.description}
              type="button"
            >
              {preset.label}
            </button>
          );
        })}
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        {axisSelect("Threads", "threads", threadScopes)}
        {axisSelect("Memory", "memory", memoryScopes)}
        {axisSelect("Credentials", "credentials", credentialScopes)}
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-950">
        <div className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
          How the agent behaves
        </div>
        {activePreset && (
          <p className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
            {activePreset.label}: {activePreset.description}
          </p>
        )}
        <ul className="mt-3 space-y-3 text-sm text-gray-700 dark:text-gray-300">
          <li>
            <span className="font-semibold text-gray-900 dark:text-gray-100">
              Threads ({scope.threads}):
            </span>{" "}
            {threadBehavior[scope.threads]}
          </li>
          <li>
            <span className="font-semibold text-gray-900 dark:text-gray-100">
              Memory ({scope.memory}):
            </span>{" "}
            {memoryBehavior[scope.memory]}
          </li>
          <li>
            <span className="font-semibold text-gray-900 dark:text-gray-100">
              Credentials ({scope.credentials}):
            </span>{" "}
            {credentialBehavior[scope.credentials]}
          </li>
        </ul>
        {needsOrg && (
          <p className="mt-3 text-sm text-amber-800 dark:text-amber-200">
            Organization is required on every request because at least one axis
            uses organization scope.
          </p>
        )}
        {scope.credentials === "custom" && (
          <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">
            Custom credentials also need a credentials resolver or endpoint in
            the identity declaration. Setting the axis alone is not enough.
          </p>
        )}
      </div>

      <div className="rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-950">
        <div className="flex items-center justify-between gap-2 border-b border-gray-200 px-3 py-2 dark:border-gray-700">
          <div className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
            Generated declaration
          </div>
          <div className="flex gap-1">
            {[
              { id: "ts", label: "TypeScript" },
              { id: "python", label: "Python" },
            ].map((option) => (
              <button
                className={
                  lang === option.id
                    ? "rounded-md bg-gray-900 px-2 py-1 text-xs font-medium text-white dark:bg-gray-100 dark:text-gray-900"
                    : "rounded-md px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                }
                key={option.id}
                onClick={() => setLang(option.id)}
                type="button"
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
        <pre className="overflow-x-auto p-3 text-xs leading-relaxed text-gray-800 dark:text-gray-200">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );
};
