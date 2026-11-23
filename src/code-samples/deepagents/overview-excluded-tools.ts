// :snippet-start: overview-excluded-tools-js
import { registerHarnessProfile } from "deepagents";

registerHarnessProfile("anthropic:claude-sonnet-4-6", {
  excludedTools: [
    "ls",
    "read_file",
    "write_file",
    "edit_file",
    "glob",
    "grep",
  ],
});
// :snippet-end:

// :remove-start:
console.log("✓ overview-excluded-tools validated");
// :remove-end:
