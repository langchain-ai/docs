from managed_deepagents import define_deep_agent
from tools.docs_edit import check_docs_coverage
from tools.github_prs import create_draft_docs_pr, get_docs_file
from tools.linear_issues import create_linear_issue, note_ship_failure_on_linear_issue
from tools.releases import (
    get_eligible_release,
    get_release_diff,
    get_release_notes,
    list_watched_products,
)
from tools.source import get_product_source_file

# Research stays on Sonnet; shipping (main agent) uses Opus for judgment-heavy edits.
_RESEARCH_MODEL = "langsmith:anthropic/claude-sonnet-4-6"
_SHIP_MODEL = "langsmith:anthropic/claude-opus-4-6"

_READ_TOOLS = [
    list_watched_products,
    get_eligible_release,
    get_release_notes,
    get_release_diff,
    get_product_source_file,
    get_docs_file,
    check_docs_coverage,
]

_WRITE_TOOLS = [
    create_linear_issue,
    create_draft_docs_pr,
    note_ship_failure_on_linear_issue,
]

_RESEARCH_SYSTEM_PROMPT = """\
You are the release-research subagent for docs-release-watch.

You investigate whether documentation updates are needed for one product release.
You are read-only: you have no Linear or GitHub PR tools.

Follow `/skills/release-research/SKILL.md`. Also load the matching product skill
(`/skills/openwiki/`, `/skills/deepagents/`, `/skills/deepagentsjs/`, or
`/skills/deepagents-code/`) for sources of truth and "what usually needs docs"
judgment only. Ignore any shipping steps in those product skills.

Primary evidence is `get_release_diff` (commits and changed files between the
previous same-prefix tag and the eligible tag), confirmed with
`get_product_source_file` at the head tag. Release notes are secondary leads.

Before setting needs_docs true, call `check_docs_coverage` with the candidate
symbols and concrete docs page paths. If every needle already appears in docs,
skip the feature (already documented) unless the docs statement is wrong.

Return one JSON research report in the shape required by the release-research
skill (product, head_tag, base_tag, features[], skipped[]). Every feature that
needs docs must include evidence that will pass the write-tool GitHub
verification gate. Do not invent symbols or paths.
"""

agent = define_deep_agent(
    name="docs-release-watch",
    model=_SHIP_MODEL,
    tools=[*_READ_TOOLS, *_WRITE_TOOLS],
    subagents=[
        {
            "name": "release-research",
            "description": (
                "Investigate an eligible product release against source diffs "
                "and current docs. Read-only. Returns a JSON feature list with "
                "evidence. Always call this before create_linear_issue or "
                "create_draft_docs_pr."
            ),
            "system_prompt": _RESEARCH_SYSTEM_PROMPT,
            "model": _RESEARCH_MODEL,
            "tools": list(_READ_TOOLS),
            "skills": ["/skills/"],
        }
    ],
)
