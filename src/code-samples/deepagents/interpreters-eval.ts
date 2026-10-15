// :remove-start:
import { ReplSession, transformForEval } from "@langchain/quickjs";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const webSearch = tool(
  async ({ query }: { query: string }) => `results for ${query}`,
  {
    name: "web_search",
    description: "Search the web.",
    schema: z.object({ query: z.string() }),
  },
);

async function main() {
  const totalsSession = ReplSession.getOrCreate("interpreters-totals-eval");
  const totalsResult = await totalsSession.eval(
    `const rows = [
  { team: "alpha", score: 8 },
  { team: "beta", score: 13 },
  { team: "alpha", score: 21 },
];
const totals = rows.reduce((acc, row) => {
  acc[row.team] = (acc[row.team] ?? 0) + row.score;
  console.log(\`\${row.team} score: \${acc[row.team]}\`)
  return acc;
}, {});
totals;`,
    5000,
  );
  const totals = totalsResult.value as { alpha?: number; beta?: number };
  if (!totalsResult.ok || totals.alpha !== 29 || totals.beta !== 13) {
    throw new Error(
      `unexpected totals eval result: ${JSON.stringify(totalsResult)}`,
    );
  }

  const ptcSession = ReplSession.getOrCreate("interpreters-ptc-eval", {
    tools: [webSearch],
  });
  const ptcResult = await ptcSession.eval(
    `const result = await tools.webSearch({ query: "deepagents interpreters" });
result;`,
    5000,
  );
  if (
    !ptcResult.ok ||
    ptcResult.value !== "results for deepagents interpreters"
  ) {
    throw new Error(`unexpected ptc call result: ${JSON.stringify(ptcResult)}`);
  }

  const parallelResult = await ptcSession.eval(
    `const topics = ["retrieval", "memory", "evaluation"];
const results = await Promise.all(
  topics.map((topic) =>
    tools.webSearch({ query: \`\${topic} best practices 2025\` }),
  ),
);
results.join("\\n\\n");`,
    5000,
  );
  if (
    !parallelResult.ok ||
    !String(parallelResult.value).includes("retrieval best practices 2025")
  ) {
    throw new Error(
      `unexpected parallel ptc result: ${JSON.stringify(parallelResult)}`,
    );
  }

  transformForEval(
    `const paths = ["src/auth.ts", "src/routes/api.ts"];
const reviews = await Promise.all(
  paths.map((path) =>
    task({
      description: \`Review \${path} for authentication issues\`,
      subagentType: "reviewer",
    }),
  ),
);
reviews.join("\\n\\n");`,
  );

  console.log("✓ interpreters-eval");
}

void main();
// :remove-end:

async function __interpretersTotalsSnippet__() {
  // :snippet-start: interpreters-totals-eval-js
  const rows = [
    { team: "alpha", score: 8 },
    { team: "beta", score: 13 },
    { team: "alpha", score: 21 },
  ];

  const totals = rows.reduce((acc, row) => {
    acc[row.team] = (acc[row.team] ?? 0) + row.score;
    console.log(`${row.team} score: ${acc[row.team]}`);
    return acc;
  }, {});

  totals;
  // :snippet-end:
}

async function __interpretersPtcCallSnippet__() {
  // :snippet-start: interpreters-ptc-call-eval-js
  const result: string = await tools.webSearch({
    query: "deepagents interpreters",
  });
  // :snippet-end:
}

async function __interpretersPtcParallelSnippet__() {
  // :snippet-start: interpreters-ptc-parallel-eval-js
  const topics = ["retrieval", "memory", "evaluation"];

  const results = await Promise.all(
    topics.map((topic) =>
      tools.webSearch({ query: `${topic} best practices 2025` }),
    ),
  );

  results.join("\n\n");
  // :snippet-end:
}

async function __interpretersTaskFanoutSnippet__() {
  // :snippet-start: interpreters-task-fanout-eval-js
  const paths = ["src/auth.ts", "src/routes/api.ts"];

  const reviews = await Promise.all(
    paths.map((path) =>
      task({
        description: `Review ${path} for authentication issues`,
        subagentType: "reviewer",
      }),
    ),
  );

  reviews.join("\n\n");
  // :snippet-end:
}
