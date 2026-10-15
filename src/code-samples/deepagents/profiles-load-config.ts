// :remove-start:
import { copyFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const here = dirname(fileURLToPath(import.meta.url));
copyFileSync(
  join(here, "../profile.yaml"),
  join(process.cwd(), "profile.yaml"),
);
// :remove-end:

// :snippet-start: profiles-load-config-js
import { readFileSync } from "fs";
import YAML from "yaml";
import { parseHarnessProfileConfig, registerHarnessProfile } from "deepagents";

const raw = YAML.parse(readFileSync("profile.yaml", "utf-8"));
registerHarnessProfile("openai", parseHarnessProfileConfig(raw));
// :snippet-end:

// :remove-start:
console.log("✓ profiles-load-config sample validated");
// :remove-end:
