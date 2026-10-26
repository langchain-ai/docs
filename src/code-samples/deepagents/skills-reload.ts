// :remove-start:
import { createDeepAgent, FilesystemBackend } from "deepagents";

const backend = new FilesystemBackend({ rootDir: process.cwd() });
const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  backend,
  skills: ["/skills/"],
});

const config = { configurable: { thread_id: "1" } };

/** Stand-in for your own check, such as scanning the run for writes under a skill source. */
function agentEditedSkills(state: unknown): boolean {
  return false;
}

console.log("✓ skills-reload sample validated");
process.exit(0);
// :remove-end:

// :snippet-start: skills-reload-invoke-js
const result = await agent.invoke(
  {
    messages: [{ role: "user", content: "What is LangGraph?" }],
    skillsMetadata: null,
  },
  config,
);
// :snippet-end:

// :snippet-start: skills-reload-update-state-js
await agent.updateState(config, { skillsMetadata: null });
// :snippet-end:

// :snippet-start: skills-reload-middleware-js
import { createMiddleware } from "langchain";
import { StateSchema } from "@langchain/langgraph";
import { skillsMetadataValue } from "deepagents";

const reloadEditedSkills = createMiddleware({
  name: "ReloadEditedSkills",
  stateSchema: new StateSchema({ skillsMetadata: skillsMetadataValue }),
  afterModel: (state) =>
    agentEditedSkills(state) ? { skillsMetadata: null } : undefined,
});
// :snippet-end:
