"""Unit tests that keep sidebar link stubs out of llms.txt and the sitemap."""

from pathlib import Path

import yaml

DOCS_DIR = Path(__file__).resolve().parents[2] / "src"


def _frontmatter(path: Path) -> dict:
    """Return the page's YAML frontmatter, or an empty dict if it has none."""
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}
    end = content.find("\n---", 4)
    if end == -1:
        return {}
    return yaml.safe_load(content[4:end]) or {}


def test_url_stubs_set_noindex() -> None:
    """Verify every page that sets `url:` in frontmatter also sets `noindex: true`.

    A `url:` page only exists to put a link in the sidebar, and it answers with a
    redirect, often to another host. Mintlify lists it in llms.txt, llms-full.txt,
    and the sitemap unless the page sets `noindex: true`. Agent-readiness scoring
    then flags the stub as a cross-host redirect with no markdown version.
    """
    violations = [
        str(path.relative_to(DOCS_DIR.parent))
        for path in sorted(DOCS_DIR.glob("**/*.mdx"))
        if (fm := _frontmatter(path)).get("url") and fm.get("noindex") is not True
    ]

    assert not violations, (
        "Pages with `url:` frontmatter must also set `noindex: true` so Mintlify "
        "keeps them out of llms.txt and the sitemap:\n" + "\n".join(violations)
    )
