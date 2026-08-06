# Proposal: `langchain deploy` for TypeScript-native agent deployment

## Executive summary

TypeScript developers should be able to deploy LangChain and LangGraph agents with the same feeling they get from Vite, Next.js, or Astro: write a typed config file, add extension packages, run one command, and get a production-ready deployment.

The proposed primitive is a TypeScript deployment compiler and CLI that lives in the LangChain ecosystem:

```ts
// langchain.config.ts
import { defineDeployment } from "langchain/deploy";
import { discord } from "@langchain/deploy-discord";
import { web } from "@langchain/deploy-web";

export default defineDeployment({
  agents: {
    support: "./src/agents/support.ts",
    research: "./src/agents/research.ts:graph",
  },
  extensions: [
    web({ agent: "support" }),
    discord({ agent: "support", route: "/discord" }),
  ],
});
```

Under the hood, this does not require a new LangSmith runtime. It compiles into the artifacts LangSmith Deployment already supports today:

- A `langgraph.json` file with `graphs`, `env`, `node_version`, `http.app`, `store`, `checkpointer`, `webhooks`, and other supported fields.
- A generated Hono app that aggregates all extension routes into the single `http.app` entrypoint LangSmith already accepts.
- Optional generated wrapper modules for intuitive agent paths that omit the `:exportName` suffix.
- CLI calls to the existing LangGraph TypeScript CLI for `dev`, `build`, `dockerfile`, `up`, and `deploy`.

The product idea is not "a new hosting platform." It is "deployment ergonomics for the hosting platform LangSmith already has."

## What LangSmith Deployment supports today

Current LangSmith Deployment has the right primitives, but they are exposed at a low level:

- Applications are described by `langgraph.json`.
- A deployment can contain multiple graphs under the `graphs` key.
- TypeScript deployments use `node_version: 20` and graph paths such as `./src/graph.ts:graph`.
- `.env` files are already supported through the `env` key, and the deploy CLI also reads API keys from `.env`.
- Cloud deployments can be created or updated with `langgraph deploy`.
- Local development works with `npx @langchain/langgraph-cli dev`.
- Docker images can be built with `npx @langchain/langgraph-cli build`.
- Custom TypeScript routes are supported by exporting a Hono app and pointing `http.app` at it.
- Agent Server already exposes durable runs, threads, assistants, streaming, stores, webhooks, MCP, A2A, CORS, route toggles, and deployment logs.

The missing piece is not capability. The missing piece is a developer-facing composition layer.

Today, if a TypeScript developer wants multiple custom endpoints or integrations, they must hand-write an `app.ts`, import every integration directly, manually wire the routes, keep `langgraph.json` in sync, remember the Hono conventions, and understand how `http.app` interacts with deployment. That is workable for advanced users, but it is not an ecosystem primitive.

## The primitive

Call the primitive **LangChain Deploy**.

It has three parts:

1. `defineDeployment()` for typed deployment configuration.
2. `defineExtension()` for reusable extension packages.
3. `langchain deploy` for generating artifacts and delegating to the existing LangGraph CLI.

This gives TypeScript developers a first-class deploy experience while preserving LangSmith's existing deployment model.

## Design principles

- Compile to current infrastructure. The package should emit `langgraph.json`, Hono route code, and optional wrapper files. It should not require Agent Server features that do not exist.
- Keep the escape hatch. Developers can still provide raw `langgraph` config, a custom Hono app, Dockerfile lines, or direct CLI flags.
- Make the common path small. A one-agent deployment should need a config file and one command.
- Make extension authors powerful but bounded. Extensions can add custom routes, UI assets, webhook handlers, CORS settings, environment requirements, and generated files. They should not replace the Agent Server runtime.
- Treat agents as named resources. Extension code should get typed graph or assistant names from the deployment context, then use the existing LangGraph SDK client.
- Prefer generation over magic. Generated artifacts should be inspectable and committed or ignored depending on project preference.

## Developer experience

### Create a deployment

```bash
npm create langchain-agent
cd my-agent
npm run deploy:dev
```

The generated project contains:

```txt
my-agent/
  langchain.config.ts
  package.json
  .env
  src/
    agents/
      support.ts
```

The initial config is small:

```ts
import { defineDeployment } from "langchain/deploy";

export default defineDeployment({
  agents: {
    support: "./src/agents/support.ts",
  },
});
```

`"./src/agents/support.ts"` is intentionally nicer than `./src/agents/support.ts:graph`. The compiler can generate a wrapper module when a file uses a default export, or resolve a named export when one is provided:

```ts
export default graph;
```

becomes:

```json
{
  "graphs": {
    "support": "./.langchain/generated/agents/support.ts:graph"
  }
}
```

If the developer wants exact control, they can write:

```ts
export default defineDeployment({
  agents: {
    support: "./src/agents/support.ts:supportGraph",
  },
});
```

### Add extensions

Extensions feel like Vite plugins:

```ts
import { defineDeployment } from "langchain/deploy";
import { discord } from "@langchain/deploy-discord";
import { web } from "@langchain/deploy-web";
import { slack } from "@acme/langchain-deploy-slack";

export default defineDeployment({
  agents: {
    support: "./src/agents/support.ts",
    research: "./src/agents/research.ts",
  },
  extensions: [
    web({
      agent: "support",
      title: "Support agent",
      route: "/",
    }),
    discord({
      agent: "support",
      route: "/discord",
    }),
    slack({
      agent: "research",
      route: "/slack/events",
    }),
  ],
});
```

The developer does not create `app.ts`. The compiler creates one generated Hono app and registers it through `http.app`.

### Deploy by environment

```ts
export default defineDeployment({
  agents: {
    support: "./src/agents/support.ts",
  },
  targets: {
    dev: {
      name: "support-agent-dev",
      type: "dev",
      env: ".env",
    },
    production: {
      name: "support-agent",
      type: "prod",
      env: ".env.production",
      hostUrl: "https://api.host.langchain.com",
    },
  },
});
```

Then:

```bash
langchain deploy --target dev
langchain deploy --target production
langchain deploy logs --target production --follow
```

This maps to current CLI behavior:

- `name` maps to `--name` or `LANGSMITH_DEPLOYMENT_NAME`.
- `type` maps to `--deployment-type`.
- `hostUrl` maps to `LANGGRAPH_HOST_URL`.
- `env` maps to the generated `langgraph.json` `env` field.
- The generated config path is passed with `-c`.

## Generated artifacts

Given:

```ts
export default defineDeployment({
  agents: {
    support: "./src/agents/support.ts",
  },
  extensions: [
    web({ agent: "support" }),
    discord({ agent: "support", route: "/discord" }),
  ],
});
```

The compiler writes:

```txt
.langchain/
  generated/
    langgraph.dev.json
    app.ts
    agents/
      support.ts
    manifest.json
    types.d.ts
```

`langgraph.dev.json`:

```json
{
  "$schema": "https://langgra.ph/schema.json",
  "node_version": "20",
  "dependencies": ["."],
  "graphs": {
    "support": "./.langchain/generated/agents/support.ts:graph"
  },
  "env": ".env",
  "http": {
    "app": "./.langchain/generated/app.ts:app"
  }
}
```

`app.ts`:

```ts
import { Hono } from "hono";
import { createDeploymentContext } from "langchain/deploy/runtime";
import extension0 from "@langchain/deploy-web";
import extension1 from "@langchain/deploy-discord";

export const app = new Hono();

const ctx = createDeploymentContext({
  app,
  agents: {
    support: {
      id: "support",
    },
  },
});

extension0.setup(ctx, { agent: "support" });
extension1.setup(ctx, { agent: "support", route: "/discord" });
```

The important trick: LangSmith only sees one Hono app. The developer sees many extensions.

## Extension API

An extension is a typed factory that receives options and returns hooks.

```ts
import { defineExtension } from "langchain/deploy";
import { Client } from "@langchain/langgraph-sdk";

export default function discord(options: DiscordOptions) {
  return defineExtension({
    name: "@langchain/deploy-discord",

    config(ctx) {
      ctx.requireEnv("DISCORD_PUBLIC_KEY");
      ctx.requireEnv("DISCORD_BOT_TOKEN");
    },

    setup(ctx) {
      ctx.route.post(options.route ?? "/discord", async (c) => {
        const event = await c.req.json();
        const client = new Client(ctx.clientOptions(c));

        const result = await client.runs.wait(null, options.agent, {
          input: {
            messages: [
              {
                role: "user",
                content: event.message,
              },
            ],
          },
          raiseError: true,
        });

        return c.json(result);
      });
    },
  });
}
```

The API should feel familiar to Vite users but map to deployment concepts:

```ts
type DeploymentExtension = {
  name: string;
  enforce?: "pre" | "post";
  apply?: "dev" | "build" | "deploy" | ((target: DeploymentTarget) => boolean);

  config?: (ctx: ConfigContext) => void | Partial<DeploymentConfig>;
  configResolved?: (ctx: ResolvedConfigContext) => void;
  generate?: (ctx: GenerateContext) => void | Promise<void>;
  setup?: (ctx: RuntimeContext) => void;
};
```

### Extension capabilities

Extensions can use current LangSmith infrastructure in these ways:

- Add Hono routes to the generated app.
- Add route-local middleware for the routes they own.
- Add static assets or generated UI bundles served by Hono routes.
- Declare required environment variables.
- Add `http.cors` settings.
- Add `webhooks` policy.
- Add `store` and `checkpointer` configuration.
- Add `dockerfile_lines` for OS-level dependencies.
- Emit generated files that are included in the project dependency.
- Expose LangGraph SDK client configuration for invoking deployed agents through the Agent Server API.

Extensions should not depend on unavailable runtime hooks. For example, TypeScript custom routes are supported today through Hono, but Python-only middleware and lifespan features should not be presented as TypeScript extension capabilities unless Agent Server adds that support.

## Agent access from extensions

Extensions should use the existing LangGraph TypeScript SDK instead of a new deployment-specific agent interface.

```ts
import { Client } from "@langchain/langgraph-sdk";

export default defineExtension({
  name: "my-extension",

  setup(ctx) {
    // `ctx` is the runtime context passed to this extension by the
    // generated deployment app. It is not a global variable.
    ctx.route.post("/ask", async (c) => {
      const client = new Client(ctx.clientOptions(c));
      const thread = client.threads.stream({ assistantId: ctx.agents.support });

      await thread.run.start({
        input: {
          messages: [{ role: "user", content: "hello" }],
        },
      });

      const output = await thread.output;
      await thread.close();

      return c.json(output);
    });
  },
});
```

Here, `"support"` is the graph ID from the `agents` map. Agent Server already treats graph IDs as default assistant IDs, and the SDK already exposes the concepts extension authors need: assistants, threads, runs, streaming, store access, and configuration.

The deployment primitive should only provide the missing context required to construct the SDK client inside generated Hono routes:

```ts
type RuntimeContext = {
  route: Hono;
  agents: {
    support: "support";
    research: "research";
  };
  clientOptions(c?: HonoContext): ConstructorParameters<typeof Client>[0];
};
```

For real-time routes and UI extensions, extension authors can use the SDK's recommended thread-centric streaming API:

```ts
const client = new Client(ctx.clientOptions(c));
const thread = client.threads.stream({ assistantId: ctx.agents.support });

await thread.run.start({
  input: {
    messages: [{ role: "user", content: "hello" }],
  },
});

for await (const message of thread.messages) {
  // Forward tokens to a browser, Discord interaction, Slack response, etc.
}

await thread.close();
```

For webhook-style or background integrations, authors can use non-streaming SDK methods such as `client.runs.create(...)`, `client.runs.wait(...)`, and `client.threads.create(...)`.

Implementation options:

- For local dev, `ctx.clientOptions(c)` can derive the current server origin from the Hono request and point `@langchain/langgraph-sdk` at the local dev server.
- For deployed routes, `ctx.clientOptions(c)` can point the SDK at the same deployment URL when available, or use relative Agent Server endpoints when the runtime supports it.
- The context should not re-expose SDK methods. It should make `new Client(...)` easy and type-safe.
- Do not use `RemoteGraph` to call the same deployment from inside a graph. Existing docs warn against same-deployment `RemoteGraph` composition because it can cause resource exhaustion. Route handlers should use the Agent Server run APIs.

This is already possible by hand today. The primitive packages the setup and keeps extension code aligned with the first-party SDK.

## CLI

The CLI should be a thin, friendly wrapper around the existing LangGraph CLI.

```bash
langchain deploy dev
langchain deploy build
langchain deploy dockerfile Dockerfile
langchain deploy up
langchain deploy --target production
langchain deploy logs --target production --follow
langchain deploy doctor
```

### `langchain deploy dev`

Generates artifacts and runs:

```bash
npx @langchain/langgraph-cli dev -c .langchain/generated/langgraph.dev.json
```

### `langchain deploy build`

Generates artifacts and runs:

```bash
npx @langchain/langgraph-cli build -c .langchain/generated/langgraph.production.json -t <tag>
```

### `langchain deploy`

Generates artifacts and runs:

```bash
npx @langchain/langgraph-cli deploy -c .langchain/generated/langgraph.production.json --name <name> --deployment-type <type>
```

### `langchain deploy doctor`

Validates the project before the slow deployment path:

- Confirms every agent path resolves.
- Confirms graph exports are usable.
- Confirms extension names are unique.
- Confirms route collisions.
- Confirms required environment variables exist for the selected target.
- Warns if a custom route shadows an Agent Server route.
- Warns if an extension adds Dockerfile lines that require Docker for local builds.
- Prints the generated `langgraph.json` path.

This is a major developer-experience win because most deployment failures today are configuration or packaging mistakes.

## Config shape

```ts
type LangChainDeploymentConfig = {
  agents: Record<string, AgentEntry>;
  extensions?: ExtensionInstance[];
  targets?: Record<string, DeploymentTarget>;

  env?: true | string | Record<string, string>;
  nodeVersion?: 20;
  apiVersion?: string;

  http?: {
    cors?: CorsConfig;
    configurableHeaders?: HeaderPolicy;
    loggingHeaders?: HeaderPolicy;
    enableCustomRouteAuth?: boolean;
    disableMeta?: boolean;
    disableAssistants?: boolean;
    disableRuns?: boolean;
    disableThreads?: boolean;
    disableStore?: boolean;
    disableUi?: boolean;
    disableMcp?: boolean;
    disableA2a?: boolean;
    disableWebhooks?: boolean;
    mountPrefix?: string;
  };

  store?: StoreConfig;
  checkpointer?: CheckpointerConfig;
  webhooks?: WebhooksConfig;
  dockerfileLines?: string[];

  raw?: Record<string, unknown>;
};
```

The `raw` escape hatch lets advanced users pass through LangGraph configuration fields before the wrapper supports first-class types.

## Environment model

By default:

```ts
defineDeployment({
  agents: {
    support: "./src/agents/support.ts",
  },
});
```

compiles with:

```json
{
  "env": ".env"
}
```

if `.env` exists.

For multiple targets:

```ts
defineDeployment({
  targets: {
    dev: { env: ".env" },
    staging: { env: ".env.staging" },
    production: { env: ".env.production" },
  },
});
```

Each target gets a generated `langgraph.<target>.json`.

Secrets remain normal LangSmith deployment environment variables. The primitive can read `.env` for local dev and CLI deploys, but it should not invent a separate secrets store. If a team uses the LangSmith UI to manage production secrets, the target can set:

```ts
production: {
  name: "support-agent",
  type: "prod",
  env: false,
}
```

## Extension examples

Extensions should be described as packaged deployment capabilities, not as thin option bags. Each extension owns a small slice of the generated Hono app and uses the LangGraph SDK to talk to one or more deployed agents. The developer configures intent: which agent, which route, and which integration-specific options. The extension handles the repeated deployment plumbing.

### Custom web UI

```ts
web({
  agent: "support",
  route: "/",
  title: "Support agent",
  theme: {
    accent: "#1C3D5A",
  },
});
```

What it does:

- Serves a small chat UI from the same Agent Server deployment.
- Opens a streaming route that calls `client.threads.stream({ assistantId: "support" })`.
- Handles thread creation, message submission, token streaming, interrupt display, and final state rendering.
- Adds any required static assets to the generated deployment output.

Why this is helpful:

Without the extension, a developer has to create a frontend bundle, serve it from Hono, define an API route, instantiate the LangGraph SDK client, stream events, and keep that custom app wired into `langgraph.json`. With the extension, a working UI is attached to the deployed agent with one config entry. The route and agent are explicit, so the compiler can catch route conflicts and invalid agent names.

### Discord

```ts
discord({
  agent: "support",
  route: "/discord/interactions",
});
```

What it does:

- Adds the endpoint Discord calls for interaction events.
- Declares required environment variables such as the Discord public key and bot token.
- Verifies the incoming request, converts a Discord message into the agent's input format, calls the configured agent with the LangGraph SDK, and formats the response for Discord.
- Optionally maps Discord channel or user IDs to LangGraph thread IDs so conversations stay stateful.

Why this is helpful:

Discord integration has a lot of boilerplate that is unrelated to agent logic: request verification, response deadlines, thread mapping, retries, and route setup. The deployment config makes the binding obvious: Discord events at `/discord/interactions` go to the `support` agent. The extension author packages the operational details once, and every agent developer reuses the same deployment behavior.

### WhatsApp or Twilio

```ts
twilioWhatsApp({
  agent: "support",
  route: "/twilio/whatsapp",
});
```

What it does:

- Adds the webhook endpoint Twilio calls for inbound WhatsApp messages.
- Declares required Twilio credentials and webhook verification settings.
- Converts inbound messages into LangGraph run input.
- Uses the SDK to continue a thread for that phone number or start a stateless run.
- Returns TwiML or calls Twilio's API to send an async response.

Why this is helpful:

The deployment becomes the integration backend. The developer does not need a separate Express app, serverless function, or queue just to connect Twilio to the agent. The extension can standardize phone-number-to-thread mapping while still letting the developer choose which deployed agent handles the conversation.

### Agent-to-app API

```ts
api({
  routes: {
    "/api/ask": {
      agent: "support",
      input: z.object({ message: z.string() }),
      stream: true,
    },
  },
});
```

What it does:

- Adds a public or private HTTP endpoint for an application frontend.
- Validates request bodies with the provided schema.
- Converts the validated body into agent input.
- Streams the result or returns a final JSON response using the SDK.
- Can generate a typed client helper for the app that calls `/api/ask`.

Why this is helpful:

Many teams do not want to expose raw Agent Server endpoints directly to their product frontend. They want an application-specific API such as `/api/ask`, `/api/triage`, or `/api/search`. This extension gives them that route without hiding LangSmith. It is still just a Hono route over Agent Server runs, but the repetitive validation and streaming glue are generated from a typed declaration.

### Deploy-time policy

```ts
policy({
  disableDocsInProduction: true,
  requireWebhookHttps: true,
  corsOrigins: ["https://app.example.com"],
});
```

What it does:

- Applies deployment configuration that already exists in `langgraph.json`.
- Sets production CORS rules.
- Disables metadata or docs routes for production targets.
- Restricts webhook destinations to HTTPS or approved domains.
- Fails `langchain deploy doctor` if a target violates the policy.

Why this is helpful:

These settings are easy to forget because they are not part of the agent's graph code. A policy extension lets a platform team publish deployment standards once and have every agent project apply them consistently. It compiles to existing `http` and `webhooks` configuration, so it does not require new LangSmith infrastructure.

## Why this is compelling

This creates a marketplace-shaped extension surface without creating a new platform surface.

Vite became powerful because framework authors could package conventions as plugins. Next.js became approachable because routing, build output, and deployment conventions are encoded into the framework. LangSmith already has the runtime for durable agents, but TypeScript developers still need to assemble deployment details manually.

LangChain Deploy can make the unit of sharing "an agent deployment extension":

- `@langchain/deploy-web`
- `@langchain/deploy-discord`
- `@langchain/deploy-slack`
- `@langchain/deploy-whatsapp`
- `@langchain/deploy-twilio`
- `@langchain/deploy-auth0`
- `@langchain/deploy-openapi`
- `@langchain/deploy-admin`

Each package is just TypeScript, Hono routes, generated files, and current LangSmith config. That means the ecosystem can move quickly without waiting for new Agent Server primitives.

## What should be out of scope

- A new runtime separate from Agent Server.
- A second deployment backend.
- A custom secrets manager.
- A new graph execution model.
- Same-deployment `RemoteGraph` composition from inside graph execution.
- TypeScript middleware or lifespan claims beyond what Agent Server supports for TypeScript custom routes.
- Automatic production secret upload unless the existing Control Plane API supports it directly.

## Implementation plan

### Phase 1: Compiler and CLI

- Add `defineDeployment()` and config types.
- Load `langchain.config.ts` with a TS runtime or bundler.
- Generate `langgraph.json`.
- Generate wrappers for default-export agents.
- Detect `.env`.
- Delegate `dev`, `build`, `up`, and `deploy` to the LangGraph CLI.
- Add `doctor`.

### Phase 2: Extension runtime

- Add `defineExtension()`.
- Generate one Hono `app.ts`.
- Add route registration, env requirements, route collision detection, and target-aware `apply`.
- Add `ctx.clientOptions()` and typed `ctx.agents` so extensions can construct `@langchain/langgraph-sdk` clients directly.
- Ship `@langchain/deploy-web` as the reference extension.

### Phase 3: Ecosystem

- Publish extension authoring docs.
- Add templates for Discord, Slack, WhatsApp, and custom UI extensions.
- Add a gallery of extension packages.
- Add generated type declarations for route and agent names.

### Phase 4: LangSmith UI integration

- Surface generated manifest metadata in deployment details if supported.
- Show extension names and routes in build logs or deployment metadata.
- Link custom routes from the deployment page.

This phase should remain optional. The core value does not depend on LangSmith UI changes.

## Open questions

- Should the package live at `langchain/deploy`, `@langchain/deploy`, or inside `@langchain/langgraph-cli`?
- Should generated artifacts be committed, ignored, or configurable?
- Should extension route order follow Vite-style `enforce`, array order only, or both?
- Should the default agent export convention prefer `default`, `graph`, or require explicit symbols in strict mode?
- Can Agent Server expose an officially supported in-process helper for custom routes to create runs without HTTP loopback?
- Should the CLI support GitHub-based deployments, or only local build and deploy flows at first?
- Should production `.env` loading be opt-in to avoid accidental secret inclusion in generated artifacts?

## The pitch

LangSmith Deployment already has the runtime. LangChain Deploy would provide the product-shaped developer interface.

The mental model becomes:

```txt
agents + extensions + targets => LangSmith deployment artifacts
```

For a TypeScript developer, that is a much stronger primitive than "write `langgraph.json`, write one custom Hono app, wire every integration by hand, then remember the right CLI flags."

It makes LangSmith Deployment feel native to the TypeScript ecosystem while staying honest about what the platform can run today.
