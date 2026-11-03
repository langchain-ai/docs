// :snippet-start: profiles-registration-js
import { registerHarnessProfile } from "deepagents";

// Set defaults for a hypothetical provider.
registerHarnessProfile("my_provider", {
  excludedTools: ["execute"],
  systemPromptSuffix: "Respond in under 500 words.",
});

// Override the prompt suffix for one model; inherit the excluded tool.
registerHarnessProfile("my_provider:my-model", {
  systemPromptSuffix: "Respond in under 100 words.",
});
// :snippet-end:

// :remove-start:
import assert from "node:assert/strict";
import { getHarnessProfile } from "deepagents";

let profile = getHarnessProfile("my_provider:my-model");
assert.ok(profile);
assert.deepEqual(new Set(profile.excludedTools), new Set(["execute"]));
assert.equal(profile.systemPromptSuffix, "Respond in under 100 words.");
const other = getHarnessProfile("my_provider:another-model");
assert.ok(other);
assert.deepEqual(new Set(other.excludedTools), new Set(["execute"]));
assert.equal(other.systemPromptSuffix, "Respond in under 500 words.");
// :remove-end:

// :snippet-start: profiles-reregister-harness-js
registerHarnessProfile("my_provider:my-model", {
  excludedTools: ["grep"],
});
// :snippet-end:

// :remove-start:
profile = getHarnessProfile("my_provider:my-model");
assert.ok(profile);
assert.deepEqual(new Set(profile.excludedTools), new Set(["execute", "grep"]));
assert.equal(profile.systemPromptSuffix, "Respond in under 100 words.");
assert.deepEqual(getHarnessProfile("my_provider:another-model"), other);
console.log("Profile registration and re-registration examples validated");
// :remove-end:
