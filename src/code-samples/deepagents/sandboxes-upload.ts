import { LangSmithSandbox } from "deepagents";
import { SandboxClient } from "langsmith/sandbox";

const client = new SandboxClient();
const lsSandbox = await client.createSandbox();
const sandbox = new LangSmithSandbox({ sandbox: lsSandbox });

// :snippet-start: deepagents-sandbox-upload-js
const encoder = new TextEncoder();
const responses = await sandbox.uploadFiles([
  ["src/index.js", encoder.encode("console.log('Hello')")],
  ["package.json", encoder.encode('{"name": "my-app"}')],
]);

// Each response indicates success or failure
for (const res of responses) {
  if (res.error) {
    console.error(`Failed to upload ${res.path}: ${res.error}`);
  }
}
// :snippet-end:

// :remove-start:
if (responses.length !== 2) {
  throw new Error("expected two upload responses");
}
try {
  console.log("✓ deepagents-sandbox-upload-js validated");
} finally {
  await client.deleteSandbox(lsSandbox.name);
}
// :remove-end:
