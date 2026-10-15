// :snippet-start: profiles-serialize-js
import { serializeProfile } from "deepagents";
// :remove-start:
import { parseHarnessProfileConfig } from "deepagents";

const profile = parseHarnessProfileConfig({
  systemPromptSuffix: "Respond briefly.",
});
const serialized = serializeProfile(profile);
if (!serialized.systemPromptSuffix) {
  throw new Error("expected systemPromptSuffix in serialized profile");
}
console.log("✓ profiles-serialize sample validated");
process.exit(0);
// :remove-end:

const data = serializeProfile(profile); // JSON-compatible object
// :snippet-end:
