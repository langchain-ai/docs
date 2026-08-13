import { LangSmithSandbox } from "deepagents";
import { SandboxClient } from "langsmith/sandbox";

const client = new SandboxClient();
const lsSandbox = await client.createSandbox();
const sandbox = new LangSmithSandbox({ sandbox: lsSandbox });

// :remove-start:
const seedEncoder = new TextEncoder();
await sandbox.uploadFiles([
  ["src/index.js", seedEncoder.encode("console.log('Hello')")],
  ["output.txt", seedEncoder.encode("done")],
]);
// :remove-end:

// :snippet-start: deepagents-sandbox-download-js
const results = await sandbox.downloadFiles(["src/index.js", "output.txt"]);

const decoder = new TextDecoder();
for (const result of results) {
  if (result.content) {
    console.log(`${result.path}: ${decoder.decode(result.content)}`);
  } else {
    console.error(`Failed to download ${result.path}: ${result.error}`);
  }
}
// :snippet-end:

// :remove-start:
if (results.length !== 2) {
  throw new Error("expected two download results");
}
try {
  console.log("✓ deepagents-sandbox-download-js validated");
} finally {
  await client.deleteSandbox(lsSandbox.name);
}
// :remove-end:
