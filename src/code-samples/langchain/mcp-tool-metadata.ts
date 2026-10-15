// :snippet-start: mcp-tool-metadata-js
import type { DynamicStructuredTool } from "@langchain/core/tools";
import type { ToolAnnotations } from "@modelcontextprotocol/client";

/** Read the MCP destructive hint from the adapter's tool metadata. */
function isDestructive(tool: DynamicStructuredTool): boolean {
  // Use optional chaining and a default so a tool missing any field returns
  // false rather than raising.
  const annotations = tool.metadata?.annotations as ToolAnnotations | undefined;
  return annotations?.destructiveHint ?? false;
}
// :snippet-end:

// :remove-start:
import assert from "node:assert/strict";
import { tool } from "@langchain/core/tools";
import { z } from "zod/v4";

const makeTool = (metadata?: Record<string, unknown>) =>
  tool(() => "No files were changed.", {
    name: "delete_file",
    description: "Fixture tool",
    schema: z.object({}),
    metadata,
  });
assert.equal(isDestructive(makeTool()), false);
assert.equal(isDestructive(makeTool({})), false);
assert.equal(isDestructive(makeTool({ annotations: {} })), false);
assert.equal(
  isDestructive(makeTool({ annotations: { destructiveHint: false } })),
  false,
);
assert.equal(
  isDestructive(makeTool({ annotations: { destructiveHint: true } })),
  true,
);
console.log("✓ mcp-tool-metadata: optional annotations and destructive hint");
// :remove-end:
