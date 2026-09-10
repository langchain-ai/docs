# Docs authoring skills

Agent skills for working in this repository. Each skill is a directory holding a
`SKILL.md`: YAML frontmatter with a `name` and a `description`, then markdown
instructions. The format is the [Agent Skills](https://agentskills.io) open
standard, so one file works across agents without modification.

## Why `.agents/skills/`

`.agents/skills/` is the project path that Cursor, Codex, GitHub Copilot, Gemini
CLI, OpenCode, Deep Agents, Droid, Kilo Code, and roughly fifteen other agents
read directly. Those agents need no install step: clone the repository and the
skills are there.

Claude Code is the exception. It reads `.claude/skills/` only, and `.claude/` is
gitignored, so link the tree once:

```bash
make skills
```

That symlinks each skill into `.claude/skills/`, so the skills stay live as the
tree changes. The target is idempotent, leaves any personal skills already in
that directory alone, and removes links whose source is gone. Run it again after
pulling if a skill was added or renamed.

For an agent that uses some other path, the [`skills`
CLI](https://github.com/vercel-labs/skills) knows the mapping:

```bash
npx skills add ./.agents/skills --skill '*' --agent <agent> --yes
```

Note that the CLI **copies** files for a local source and `npx skills update`
does not refresh a local source, so a copy installed this way goes stale when
the tree changes. Re-run the command after pulling, or symlink instead.

## Available skills

| Skill | Use it for |
|-------|-----------|
| `add-docs-page` | Adding, moving, renaming, or deleting a page: source directory, frontmatter, `src/docs.json` navigation, redirects, verification. |
| `docs-review` | Reviewing changed prose against Vale and the style guide, reporting the rule each finding breaks. Runs on a PR, a branch, or the working tree. |
| `document-tooling-in-notion` | Recording new or changed tooling on the internal Notion pages: which page owns the topic, what stays in the repo, how to edit safely. |

Three more skills live in `.deepagents/skills/` (`docs-code-samples`,
`submit-integration`, `update-integrations-prs`). They stay there for now
because `.github/workflows/integration-submission.yml` invokes
`submit-integration` through the `langchain-ai/deepagents` action, which resolves
that path.

## What belongs in a skill, and what belongs in AGENTS.md

`AGENTS.md` and `CLAUDE.md` are always-on context: every rule in them costs
tokens on every task, whether or not the task is related. A skill's
`description` is the only part loaded up front, and the body loads when the
skill is invoked.

So the split is:

- **`AGENTS.md` keeps invariants** that apply to any edit: critical rules, the
  style guide, frontmatter, syntax, the navigation map.
- **Skills own procedures** that only some tasks need: multi-step workflows with
  decision points, tool calls, and verification steps.

Skills **link into** `AGENTS.md` rather than restating it. The guidelines
already fan out into four derived files kept in sync by hand, with a CI job
enforcing that `AGENTS.md` and `CLAUDE.md` stay byte-identical. A skill that
copies the style guide becomes a fifth copy that drifts silently.

## Adding a skill

1. Create `.agents/skills/<name>/SKILL.md`. Use a verb-noun name matching the
   directory name.
2. Write the `description` in the vocabulary a person would use to ask for the
   task, not as a topic label. It is the only thing an agent matches against, so
   "add a new doc, move or rename a page, update the nav" beats "helps with
   documentation."
3. Keep the body to one workflow. Split rather than branch across unrelated
   tasks.
4. Validate the frontmatter:

   ```bash
   claude plugin validate .agents/skills --strict
   ```

   Validate the real path. The validator does not follow symlinks, so pointing
   it at `.claude/skills` reports a warning instead of checking anything. A
   session does follow them.

5. Add a row to the table above.

Personal skills belong in `~/.claude/skills/`, not here.
