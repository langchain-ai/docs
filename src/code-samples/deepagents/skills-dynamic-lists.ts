// :snippet-start: skills-dynamic-lists-js
import { createDeepAgent } from "deepagents";

const SKILLS_BY_ROLE: Record<string, string[]> = {
  engineering: ["/skills/shared/", "/skills/engineering/"],
  data: ["/skills/shared/", "/skills/data/"],
  support: ["/skills/shared/", "/skills/support/"],
};

function createAgentForUser(userRole: string) {
  // KEEP MODEL
  return createDeepAgent({
    model: "anthropic:claude-sonnet-4-6",
    skills: SKILLS_BY_ROLE[userRole] ?? [],
  });
}
// :snippet-end:

// :remove-start:
const agent = await createAgentForUser("engineering");
if (!agent) throw new Error("agent not created");
console.log("✓ skills-dynamic-lists sample validated");
// :remove-end:
