from managed_deepagents import define_deep_agent

from tools.github_prs import create_draft_docs_pr
from tools.linear_issues import create_linear_issue
from tools.releases import get_eligible_release, get_release_notes, list_watched_products

agent = define_deep_agent(
    name="docs-release-watch",
    model="langsmith:anthropic/claude-sonnet-4-6",
    tools=[
        list_watched_products,
        get_eligible_release,
        get_release_notes,
        create_linear_issue,
        create_draft_docs_pr,
    ],
)
