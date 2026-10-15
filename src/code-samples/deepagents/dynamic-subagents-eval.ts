// :remove-start:
import { ReplSession, transformForEval } from "@langchain/quickjs";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const globTool = tool(
  async ({ pattern }: { pattern: string }) =>
    "src/routes/api.ts\nsrc/routes/auth.ts",
  {
    name: "glob",
    description: "Find files matching a glob pattern",
    schema: z.object({ pattern: z.string() }),
  },
);

async function main() {
  transformForEval(
    `const review = await task({
  description: "Review src/auth/login.ts for auth issues. Cite line numbers.",
  subagentType: "reviewer",
  responseSchema: {
    type: "object",
    properties: {
      issues: { type: "array", items: { type: "object", properties: {
        file: { type: "string" }, line: { type: "number" },
        severity: { type: "string" }, description: { type: "string" },
      }}},
    },
  },
});
const critical = review.issues.filter((issue) => issue.severity === "high");
critical;`,
  );

  transformForEval(
    `const SPECIALIST = { bug: "bug-fixer", feature: "feature-analyst", question: "support-agent" };
const tickets = [{ category: "bug", text: "login fails" }];
const handled = await Promise.all(
  tickets.map((ticket) =>
    task({
      description: \`Handle this \${ticket.category}:\\n\${ticket.text}\`,
      subagentType: SPECIALIST[ticket.category],
    }),
  ),
);
handled;`,
  );

  const fanoutSession = ReplSession.getOrCreate("dynamic-subagents-fanout-eval", {
    tools: [globTool],
  });
  const fanoutResult = await fanoutSession.eval(
    `const files = (await tools.glob({ pattern: "src/routes/**/*.ts" }))
  .split("\\n")
  .filter(Boolean);
files.length;`,
    5000,
  );
  if (!fanoutResult.ok || fanoutResult.value !== 2) {
    throw new Error(`unexpected fanout glob result: ${JSON.stringify(fanoutResult)}`);
  }

  transformForEval(
    `const files = (await tools.glob({ pattern: "src/routes/**/*.ts" }))
  .split("\\n")
  .filter(Boolean);
const reviews = await Promise.all(
  files.map((file) =>
    task({
      description: \`Review \${file} for authentication issues. Cite line numbers.\`,
      subagentType: "reviewer",
      responseSchema: issuesSchema,
    }),
  ),
);
const issues = reviews.flatMap((r) => r.issues);
issues;`,
  );

  transformForEval(
    `const { findings } = await task({
  description: "Audit the payments module for vulnerabilities.",
  subagentType: "reviewer",
  responseSchema: findingsSchema,
});
const verdicts = await Promise.all(
  findings.map((f) =>
    task({
      description: \`Verify \${f.file}:\${f.line} (\${f.description}). Confirm or refute.\`,
      subagentType: "verifier",
      responseSchema: verdictSchema,
    }),
  ),
);
const confirmed = findings.filter((_, i) => verdicts[i]?.confirmed);
confirmed;`,
  );

  transformForEval(
    `const proposals = await Promise.all(
  [1, 2, 3].map((n) =>
    task({
      description: \`Approach \${n}: redesign the orders schema, with tradeoffs.\`,
      subagentType: "architect",
      responseSchema: designSchema,
    }),
  ),
);
const best = proposals.sort((a, b) => score(b) - score(a))[0];
best;`,
  );

  transformForEval(
    `let bracket = await Promise.all(
  [1, 2, 3, 4, 5].map((n) =>
    task({ description: \`Rewrite processOrder for readability (variant \${n}).\`, subagentType: "writer" }),
  ),
);
while (bracket.length > 1) {
  const winners = [];
  for (let i = 0; i < bracket.length; i += 2) {
    if (bracket[i + 1] === undefined) { winners.push(bracket[i]); break; }
    const { winner } = await task({
      description: \`Pick the more readable:\\n\\nA:\\n\${bracket[i]}\\n\\nB:\\n\${bracket[i + 1]}\`,
      subagentType: "judge",
      responseSchema: pickSchema,
    });
    winners.push(winner === "A" ? bracket[i] : bracket[i + 1]);
  }
  bracket = winners;
}
bracket[0];`,
  );

  transformForEval(
    `const seen = new Set();
const found = [];
while (true) {
  const { items } = await task({
    description: \`Find dead code. Already found: \${[...seen].join(", ") || "(none)"}.\`,
    subagentType: "analyzer",
    responseSchema: itemsSchema,
  });
  const fresh = items.filter((i) => !seen.has(i.id));
  if (fresh.length === 0) break;
  for (const i of fresh) { seen.add(i.id); found.push(i); }
}
found;`,
  );

  console.log("✓ dynamic-subagents-eval");
}

void main();
// :remove-end:

async function __dynamicSubagentsTaskApiSnippet__() {
  // :snippet-start: dynamic-subagents-task-api-eval-js
  const review = await task({
    description: "Review src/auth/login.ts for auth issues. Cite line numbers.",
    subagentType: "reviewer",
    responseSchema: {
      type: "object",
      properties: {
        issues: { type: "array", items: { type: "object", properties: {
          file: { type: "string" }, line: { type: "number" },
          severity: { type: "string" }, description: { type: "string" },
        }}},
      },
    },
  });

  // With responseSchema, the result is already a typed value, so no JSON.parse is needed.
  const critical = review.issues.filter((issue) => issue.severity === "high");
  // :snippet-end:
}

async function __dynamicSubagentsClassifyEvalSnippet__() {
  // :snippet-start: dynamic-subagents-classify-eval-js
  // The agent has already classified each ticket; this routes every item to
  // the right specialist and collects the handled results.
  const SPECIALIST = { bug: "bug-fixer", feature: "feature-analyst", question: "support-agent" };

  const handled = await Promise.all(
    tickets.map((ticket) =>
      task({
        description: `Handle this ${ticket.category}:\n${ticket.text}`,
        subagentType: SPECIALIST[ticket.category],
      }),
    ),
  );
  // ... group handled results by category into a single triage report
  handled;
  // :snippet-end:
}

async function __dynamicSubagentsFanoutEvalSnippet__() {
  // :snippet-start: dynamic-subagents-fanout-eval-js
  // One reviewer per file, dispatched in parallel, then findings merged.
  const files = (await tools.glob({ pattern: "src/routes/**/*.ts" }))
    .split("\n")
    .filter(Boolean);

  const reviews = await Promise.all(
    files.map((file) =>
      task({
        description: `Review ${file} for authentication issues. Cite line numbers.`,
        subagentType: "reviewer",
        responseSchema: issuesSchema, // -> { issues: [{ file, line, severity }] }
      }),
    ),
  );

  const issues = reviews.flatMap((r) => r.issues);
  // ... sort by severity, drop duplicates, summarize the top risks
  issues;
  // :snippet-end:
}

async function __dynamicSubagentsAdversarialEvalSnippet__() {
  // :snippet-start: dynamic-subagents-adversarial-eval-js
  // Pass 1: audit. Pass 2: verify each finding independently; keep only confirmed.
  const { findings } = await task({
    description: "Audit the payments module for vulnerabilities.",
    subagentType: "reviewer",
    responseSchema: findingsSchema, // -> { findings: [{ id, file, line, description }] }
  });

  const verdicts = await Promise.all(
    findings.map((f) =>
      task({
        description: `Verify ${f.file}:${f.line} (${f.description}). Confirm or refute.`,
        subagentType: "verifier",
        responseSchema: verdictSchema, // -> { confirmed: boolean }
      }),
    ),
  );

  const confirmed = findings.filter((_, i) => verdicts[i]?.confirmed);
  // ... report only the confirmed vulnerabilities
  confirmed;
  // :snippet-end:
}

async function __dynamicSubagentsGenerateEvalSnippet__() {
  // :snippet-start: dynamic-subagents-generate-eval-js
  // Generate independent proposals in parallel, then score and keep the best.
  const proposals = await Promise.all(
    [1, 2, 3].map((n) =>
      task({
        description: `Approach ${n}: redesign the orders schema, with tradeoffs.`,
        subagentType: "architect",
        responseSchema: designSchema, // -> { design, tradeoffs }
      }),
    ),
  );

  // ... score each proposal against the requirements
  const best = proposals.sort((a, b) => score(b) - score(a))[0];
  best;
  // :snippet-end:
}

async function __dynamicSubagentsTournamentEvalSnippet__() {
  // :snippet-start: dynamic-subagents-tournament-eval-js
  // Generate variants, then judge pairwise until a single winner remains.
  let bracket = await Promise.all(
    [1, 2, 3, 4, 5].map((n) =>
      task({ description: `Rewrite processOrder for readability (variant ${n}).`, subagentType: "writer" }),
    ),
  );

  while (bracket.length > 1) {
    const winners = [];
    for (let i = 0; i < bracket.length; i += 2) {
      if (bracket[i + 1] === undefined) { winners.push(bracket[i]); break; }
      const { winner } = await task({
        description: `Pick the more readable:\n\nA:\n${bracket[i]}\n\nB:\n${bracket[i + 1]}`,
        subagentType: "judge",
        responseSchema: pickSchema, // -> { winner: "A" | "B" }
      });
      winners.push(winner === "A" ? bracket[i] : bracket[i + 1]);
    }
    bracket = winners;
  }
  bracket[0]; // the winning rewrite
  // :snippet-end:
}

async function __dynamicSubagentsLoopEvalSnippet__() {
  // :snippet-start: dynamic-subagents-loop-eval-js
  // Keep dispatching rounds, deduping against what's found, until a round adds nothing.
  const seen = new Set();
  const found = [];

  while (true) {
    const { items } = await task({
      description: `Find dead code. Already found: ${[...seen].join(", ") || "(none)"}.`,
      subagentType: "analyzer",
      responseSchema: itemsSchema, // -> { items: [{ id, file }] }
    });
    const fresh = items.filter((i) => !seen.has(i.id));
    if (fresh.length === 0) break; // converged: nothing new
    for (const i of fresh) { seen.add(i.id); found.push(i); }
  }
  found;
  // :snippet-end:
}

void __dynamicSubagentsTaskApiSnippet__;
void __dynamicSubagentsClassifyEvalSnippet__;
void __dynamicSubagentsFanoutEvalSnippet__;
void __dynamicSubagentsAdversarialEvalSnippet__;
void __dynamicSubagentsGenerateEvalSnippet__;
void __dynamicSubagentsTournamentEvalSnippet__;
void __dynamicSubagentsLoopEvalSnippet__;
