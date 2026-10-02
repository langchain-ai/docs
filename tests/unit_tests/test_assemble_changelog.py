from __future__ import annotations

from pathlib import Path

from scripts.assemble_changelog import Fragment, render_bullet


def test_render_bullet_normalizes_prose_for_vale() -> None:
    fragment = Fragment(
        path=Path("fragment.yaml"),
        title="Example",
        body=(
            "Use the drill-down view — the file url accepts 100 MB uploads. "
            "GET /v2/runs/{run_id}/url returns the URL; preserve "
            "`get_url — 100 MB`."
        ),
        components=["fleet"],
        flag=None,
        status="ready",
    )

    assert (
        render_bullet(fragment)
        == (
            "- Use the detailed view—the file URL accepts 100MB uploads. "
            "`GET /v2/runs/{run_id}/url` returns the URL; preserve "
            "`get_url — 100 MB`."
        )
    )
