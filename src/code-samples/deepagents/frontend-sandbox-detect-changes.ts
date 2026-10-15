type FileSnapshot = Record<string, string>;

// :snippet-start: frontend-sandbox-detect-changes-js
function detectChanges(
  current: FileSnapshot,
  original: FileSnapshot,
): Set<string> {
  const changed = new Set<string>();
  for (const [path, content] of Object.entries(current)) {
    if (original[path] !== content) changed.add(path);
  }
  for (const path of Object.keys(original)) {
    if (!(path in current)) changed.add(path);
  }
  return changed;
}
// :snippet-end:

// :remove-start:
const changed = detectChanges({ "/app/a.js": "new" }, { "/app/a.js": "old" });
if (!changed.has("/app/a.js")) {
  throw new Error("expected changed path");
}
console.log("✓ frontend-sandbox-detect-changes-js validated");
// :remove-end:
