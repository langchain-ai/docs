"""Tests for scripts/changelog_pipeline.py helpers that need no network or model."""

from __future__ import annotations

import datetime as dt
import json
import re
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

from scripts import changelog_pipeline as cp

if TYPE_CHECKING:
    from pathlib import Path


def test_week_label_same_and_spanning_month() -> None:
    """Labels match the changelog's existing week format."""
    assert (
        cp._week_label(dt.date(2026, 10, 5), dt.date(2026, 10, 12))
        == "October 5-12, 2026"
    )
    assert (
        cp._week_label(dt.date(2026, 9, 28), dt.date(2026, 10, 5))
        == "September 28-October 5, 2026"
    )


@pytest.mark.parametrize(
    "today", [dt.date(2026, 10, 12), dt.date(2026, 10, 13), dt.date(2026, 10, 18)]
)
def test_default_window_ends_on_most_recent_monday(today: dt.date) -> None:
    """The default window is the week that ended on the last Monday."""
    assert cp._default_window(today) == (dt.date(2026, 10, 5), dt.date(2026, 10, 12))


def test_strict_closes_nested_objects() -> None:
    """Structured outputs need every object closed."""
    schema = {
        "type": "object",
        "properties": {"a": {"type": "array", "items": {"type": "object"}}},
    }
    strict = cp._strict(schema)
    assert strict["additionalProperties"] is False
    assert strict["properties"]["a"]["items"]["additionalProperties"] is False
    assert "additionalProperties" not in schema  # the input is not mutated


def test_strict_turns_type_lists_into_any_of() -> None:
    """A nullable field uses anyOf, which structured outputs support."""
    schema = {"type": "object", "properties": {"flag": {"type": ["string", "null"]}}}
    flag = cp._strict(schema)["properties"]["flag"]
    assert flag == {"anyOf": [{"type": "string"}, {"type": "null"}]}


@pytest.mark.parametrize(
    ("body", "want"),
    [
        ("## Description\n\nFlag: none\n", ["none"]),
        ("Flag: custom_apps_editing", ["custom_apps_editing"]),
        ("The Flag: line goes on its own line", []),
        ("```\nFlag: none\n```\n\nFlag: new_feature\n", ["new_feature"]),
        ("~~~md\nFlag: none\n~~~\nFlag: new_feature", ["new_feature"]),
        ("<!-- e.g.\nFlag: none\n-->\nFlag: new_feature", ["new_feature"]),
        ("> Flag: none\n\nFlag: new_feature", ["new_feature"]),
        ("    Flag: none\n\nFlag: new_feature", ["new_feature"]),
        ("Flag: none\nFlag: None", ["none"]),
        ("Flag: none\nFlag: new_feature", ["none", "new_feature"]),
    ],
)
def test_declared_flags_matches_langdev_rules(body: str, want: list[str]) -> None:
    """Flag: parsing matches the langdev `changelog` check."""
    assert cp._declared_flags(body) == want


def test_declared_flag_prefers_flag_line_then_fragment() -> None:
    """The Flag: line wins; fragments cover older PRs; conflicts hold."""
    fragment = [{"data": {"flag": "legacy_flag"}}]
    assert cp._declared_flag({"body": "Flag: none", "fragments": fragment}) is None
    assert (
        cp._declared_flag({"body": "Flag: new_feature", "fragments": []})
        == "new_feature"
    )
    assert cp._declared_flag({"body": "", "fragments": fragment}) == "legacy_flag"
    assert (
        cp._declared_flag({"body": "Flag: a_flag\nFlag: b_flag", "fragments": []})
        == cp.CONFLICTING_FLAGS
    )


def test_insert_update_goes_before_the_first_block(tmp_path: Path) -> None:
    """New weeks go above the newest existing week."""
    page = tmp_path / "changelog.mdx"
    page.write_text(
        '---\ntitle: X\n---\n\nIntro.\n\n<Update label="old">\n- a\n</Update>\n'
    )
    cp._insert_update(page, '<Update label="new">\n- b\n</Update>\n')
    text = page.read_text()
    assert text.index('label="new"') < text.index('label="old"')
    assert text.startswith('---\ntitle: X\n---\n\nIntro.\n\n<Update label="new">')


def test_apply_renames_whole_words_only() -> None:
    """Renames replace whole words only."""
    assert (
        cp._apply_renames("Polly now opens in the sidepane.")
        == "LangSmith Chat now opens in the sidepane."
    )
    assert cp._apply_renames("Pollyanna stays.") == "Pollyanna stays."


def test_ticket_re_skips_model_names() -> None:
    """Ticket IDs are caught; model names are not."""
    assert cp.TICKET_RE.search("Fixed in LSO-4430.")
    assert not cp.TICKET_RE.search("Now uses GPT-6 by default.")
    assert not cp.TICKET_RE.search("now uses gpt-6.1-sol")


def test_custom_headers_parses_name_value_lines() -> None:
    """Gateway headers come one per line; blank and malformed lines are skipped."""
    raw = "X-Gateway-Key: abc:123\n\nnot a header\n  X-Team : docs  "
    assert cp._custom_headers(raw) == {"X-Gateway-Key": "abc:123", "X-Team": "docs"}
    assert cp._custom_headers(None) == {}


class _FakeStream:
    """Stands in for the SDK's message stream context manager."""

    def __init__(self, message: SimpleNamespace) -> None:
        self._message = message

    def __enter__(self) -> _FakeStream:  # noqa: PYI034 - test double
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def get_final_message(self) -> SimpleNamespace:
        return self._message


def test_claude_api_parses_structured_output_and_prices_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The API path streams, sends a closed schema, caches, and prices usage."""
    calls = {}

    class FakeMessages:
        def stream(self, **kwargs: object) -> _FakeStream:
            calls.update(kwargs)
            return _FakeStream(
                SimpleNamespace(
                    stop_reason="end_turn",
                    content=[
                        SimpleNamespace(type="thinking", thinking=""),
                        SimpleNamespace(
                            type="text", text=json.dumps({"tier": "announce"})
                        ),
                    ],
                    usage=SimpleNamespace(
                        input_tokens=1_000_000,
                        output_tokens=1_000_000,
                        cache_creation_input_tokens=0,
                        cache_read_input_tokens=1_000_000,
                    ),
                )
            )

    monkeypatch.setattr(cp, "_api_client", SimpleNamespace(messages=FakeMessages()))
    schema = {"type": "object", "properties": {"flag": {"type": ["string", "null"]}}}
    out, meta = cp._claude_api("system", schema, "prompt", "haiku")
    assert out == {"tier": "announce"}
    assert calls["model"] == "claude-haiku-5-5"
    assert calls["max_tokens"] == cp.API_MAX_TOKENS
    sent = calls["output_config"]["format"]["schema"]
    assert sent["additionalProperties"] is False
    assert sent["properties"]["flag"] == {
        "anyOf": [{"type": "string"}, {"type": "null"}]
    }
    assert calls["system"][0]["cache_control"] == {"type": "ephemeral"}
    # $0.10 input + $0.50 output + 1M cache reads at a tenth of the input price.
    assert meta["cost_usd"] == pytest.approx(0.10 + 0.50 + 0.01)


@pytest.mark.parametrize("stop_reason", ["refusal", "max_tokens"])
def test_claude_api_raises_unless_the_turn_ended(
    monkeypatch: pytest.MonkeyPatch, stop_reason: str
) -> None:
    """A refusal or a truncated response is an error, not a partial result."""

    class FakeMessages:
        def stream(self, **_: object) -> _FakeStream:
            return _FakeStream(
                SimpleNamespace(stop_reason=stop_reason, content=[], usage=None)
            )

    monkeypatch.setattr(cp, "_api_client", SimpleNamespace(messages=FakeMessages()))
    with pytest.raises(RuntimeError, match=stop_reason):
        cp._claude_api("system", {"type": "object"}, "prompt", "sonnet")


def test_release_held_by_flag_state() -> None:
    """Rolled-out and archived flags release; pending, missing, and conflicts stay."""
    held = {
        "1": {"flag": "shipped", "title": "a"},
        "2": {"flag": "cleaned_up", "title": "b"},
        "3": {"flag": "pending", "title": "c"},
        "4": {"flag": "gone", "title": "d"},
        "5": {"flag": cp.CONFLICTING_FLAGS, "title": "e"},
    }
    flags = {
        "shipped": {"rolled_out": True, "archived": False},
        "cleaned_up": {"rolled_out": False, "archived": True},
        "pending": {"rolled_out": False, "archived": False},
    }
    released, kept = cp._release_held(held, flags)
    assert sorted(released) == ["1", "2"]
    assert "confirm it shipped" in released["2"]
    assert sorted(kept) == ["3", "4", "5"]
    assert "not found in Eppo" in kept["4"]


def test_write_held_orders_by_pr_number(tmp_path: Path) -> None:
    """The held list is written in PR order, so weekly diffs stay small."""
    path = tmp_path / "held.json"
    cp._write_held(path, {"100": {"flag": "a"}, "9": {"flag": "b"}})
    assert list(json.loads(path.read_text())) == ["9", "100"]
    assert cp._load_held(path) == {"9": {"flag": "b"}, "100": {"flag": "a"}}
    assert cp._load_held(tmp_path / "missing.json") == {}


def test_list_feat_fix_filters_by_merge_date_and_stops_paging(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Merged feat/fix PRs in the window are kept; the end date is exclusive."""

    def pr(number: int, title: str, merged: str | None, updated: str) -> dict:
        return {
            "number": number,
            "title": title,
            "merged_at": merged,
            "updated_at": updated,
        }

    first = [pr(1, "feat: in window", "2026-10-06T10:00:00Z", "2026-10-13T00:00:00Z")]
    first += [
        pr(2, "chore: wrong type", "2026-10-06T10:00:00Z", "2026-10-12T00:00:00Z")
    ]
    first += [pr(3, "fix: closed unmerged", None, "2026-10-11T00:00:00Z")]
    first += [
        pr(4, "fix: after window", "2026-10-14T00:00:00Z", "2026-10-14T00:00:00Z")
    ]
    # Merged on the window's end Monday: belongs to the next week.
    first += [pr(7, "fix: end Monday", "2026-10-12T09:00:00Z", "2026-10-12T09:00:00Z")]
    first += [pr(100 + i, "docs: x", None, "2026-10-10T00:00:00Z") for i in range(95)]
    second = [pr(5, "fix: old", "2026-09-30T00:00:00Z", "2026-10-01T00:00:00Z")] * 100
    pages = [first, second, [pr(6, "feat: never read", "2026-10-06T00:00:00Z", "x")]]
    calls = []

    def fake_run(argv: list[str], **_: object) -> str:
        calls.append(argv)
        return json.dumps(pages[len(calls) - 1])

    monkeypatch.setattr(cp, "_run", fake_run)
    got = cp._list_feat_fix(dt.date(2026, 10, 5), dt.date(2026, 10, 12))
    assert got == [1]
    assert len(calls) == 2  # the second page ends before the window, so paging stops


WEEK = "October 5-12, 2026"
PAGE = (
    "---\ntitle: X\n---\n\n"
    f'<Update label="{WEEK}" '
    'rss={{ title: "2026-10-05 - LangSmith Cloud update" }}>\n\n'
    "## Highlights\n\n- **A**: a.\n\n"
    "## Tracing\n\n- t1\n\n"
    "## Fixes and improvements\n\n"
    '<Accordion title="Show all fixes">\n\n- f1\n\n</Accordion>\n\n'
    "</Update>\n\n"
    '<Update label="older">\n\n- old\n\n</Update>\n'
)


def _item(layer: str, line: str, section: str = "", product: str = "cloud") -> dict:
    return {
        "id": "R1",
        "product": product,
        "layer": layer,
        "section": section,
        "line": line,
        "reasons": ["why"],
        "prs": [1],
        "added": False,
    }


def test_insert_entry_appends_to_matching_sections() -> None:
    """Each layer lands at the end of the section the renderer would put it in."""
    text = cp._insert_entry(PAGE, WEEK, "2026-10-05", _item("highlight", "- **B**: b."))
    text = cp._insert_entry(
        text, WEEK, "2026-10-05", _item("change", "- t2", "Tracing")
    )
    text = cp._insert_entry(text, WEEK, "2026-10-05", _item("fix", "- f2"))
    assert "## Highlights\n\n- **A**: a.\n- **B**: b.\n\n## Tracing" in text
    assert "## Tracing\n\n- t1\n- t2\n\n## Fixes and improvements" in text
    assert "- f1\n- f2\n\n</Accordion>" in text
    assert text.endswith('<Update label="older">\n\n- old\n\n</Update>\n')


def test_insert_entry_adds_missing_sections() -> None:
    """A new section goes before the fixes; a new highlight section goes first."""
    text = cp._insert_entry(
        PAGE, WEEK, "2026-10-05", _item("change", "- d1", "Deployment")
    )
    assert "- t1\n\n## Deployment\n\n- d1\n\n## Fixes and improvements" in text
    bare = PAGE.replace("## Highlights\n\n- **A**: a.\n\n", "")
    text = cp._insert_entry(bare, WEEK, "2026-10-05", _item("highlight", "- **B**: b."))
    assert (
        'LangSmith Cloud update" }}>\n\n## Highlights\n\n- **B**: b.\n\n## Tracing'
        in text
    )


def test_insert_entry_starts_a_block_and_is_idempotent() -> None:
    """A product with no block this week gets one on top; a repeat insert is a no-op."""
    page = '---\ntitle: X\n---\n\n<Update label="older">\n\n- old\n\n</Update>\n'
    item = _item("fix", "- f1", product="fleet")
    text = cp._insert_entry(page, WEEK, "2026-10-05", item)
    assert text.index(f'label="{WEEK}"') < text.index('label="older"')
    assert "Fleet product update" in text
    assert (
        f"{cp.FIXES_HEADING}\n\n{cp.FIXES_OPEN}\n\n- f1\n\n</Accordion>\n\n</Update>"
        in text
    )
    assert cp._insert_entry(text, WEEK, "2026-10-05", item) == text


def test_ticked_ids_reads_only_checked_todo_ids() -> None:
    """Only a ticked to-do's leading ID counts; its text is never used."""

    def todo(text: str, *, checked: bool) -> dict:
        return {
            "type": "to_do",
            "to_do": {"checked": checked, "rich_text": [{"plain_text": text}]},
        }

    blocks = [
        todo("R1 · cloud · Tracing: x", checked=True),
        todo("R2 · cloud · fix: y", checked=False),
        todo("Rx not an id", checked=True),
        {"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "R3"}]}},
    ]
    assert cp._ticked_ids(blocks) == {"R1"}


def _review_data(still: int = 2) -> dict:
    return {
        "label": WEEK,
        "since": "2026-10-05",
        "items": [_item("change", "- t2", "Tracing")],
        "ungrouped": [{"pr": 5, "title": "fix: x"}],
        "released": [{"pr": 6, "title": "Y", "why": "flag z fully rolled out"}],
        "newly_held": [{"pr": 7, "flag": "f", "title": "feat: z"}],
        "still_held": [{"pr": n, "title": "s", "why": "w"} for n in range(still)],
    }


def test_review_blocks_put_the_decision_first() -> None:
    """The callout and the to-dos come before the reference sections."""
    blocks = cp._review_blocks(_review_data(), "https://github.com/o/r/pull/42")
    assert blocks[0]["type"] == "callout"
    assert "PR #42" in blocks[0]["callout"]["rich_text"][0]["text"]["content"]
    kinds = [b["type"] for b in blocks]
    assert kinds.index("to_do") < kinds.index("heading_1", kinds.index("to_do"))
    todo = blocks[kinds.index("to_do")]["to_do"]
    assert todo["rich_text"][0]["text"]["content"].startswith(
        "R1 · cloud · Tracing: t2"
    )
    # Notion takes two levels of nesting in one request.
    assert all("children" not in c.get(c["type"], {}) for c in todo["children"])


def test_review_blocks_cap_the_still_held_toggle() -> None:
    """A toggle holds at most one request's worth of children."""
    blocks = cp._review_blocks(_review_data(still=150), "https://x/pull/1")
    toggle = blocks[-1]["heading_2"]
    assert toggle["is_toggleable"] is True
    assert len(toggle["children"]) == cp.NOTION_BATCH
    assert (
        "And 51 more"
        in toggle["children"][-1]["bulleted_list_item"]["rich_text"][0]["text"][
            "content"
        ]
    )


def test_rich_splits_long_text() -> None:
    """Notion rejects a text item over 2,000 characters."""
    chunks = cp._rich("x" * 4500)
    assert [len(c["text"]["content"]) for c in chunks] == [2000, 2000, 500]


def test_review_sync_inserts_ticked_entries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ticked entries go into the PR checkout once and the row is marked Synced."""
    for target in cp.CHANGELOG_TARGETS.values():
        path = tmp_path / target.relative_to(cp._REPO_ROOT)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(PAGE)
    review = tmp_path / cp.REVIEW_FILE.relative_to(cp._REPO_ROOT)
    review.parent.mkdir(parents=True, exist_ok=True)
    data = _review_data()
    data["items"].append(dict(_item("fix", "- f9"), id="R2"))
    review.write_text(json.dumps(data))
    page_id = "0" * 32
    calls = []

    def fake_notion(method: str, path: str, body: dict | None = None) -> dict:
        calls.append((method, path, body))
        if path.endswith("/query"):
            return {"results": [{"id": page_id, "url": "https://notion/x"}]}
        if path.startswith("/blocks/"):
            return {
                "results": [
                    {
                        "type": "to_do",
                        "to_do": {
                            "checked": True,
                            "rich_text": [{"plain_text": "R1 · x"}],
                        },
                    }
                ],
                "has_more": False,
            }
        return {}

    monkeypatch.setattr(cp, "_notion", fake_notion)
    args = SimpleNamespace(pr_url="https://github.com/o/r/pull/1", root=str(tmp_path))
    cp.cmd_review_sync(args)
    cloud = (
        tmp_path / cp.CHANGELOG_TARGETS["cloud"].relative_to(cp._REPO_ROOT)
    ).read_text()
    assert "- t1\n- t2\n" in cloud
    assert "- f9" not in cloud
    saved = json.loads(review.read_text())
    assert [i["added"] for i in saved["items"]] == [True, False]
    assert calls[-1] == (
        "PATCH",
        f"/pages/{page_id}",
        {"properties": {"Status": {"select": {"name": "Synced"}}}},
    )
    cp.cmd_review_sync(args)  # a second sync adds nothing
    assert (
        cloud
        == (
            tmp_path / cp.CHANGELOG_TARGETS["cloud"].relative_to(cp._REPO_ROOT)
        ).read_text()
    )


def test_notion_id_rejects_paths() -> None:
    """Only a Notion ID reaches an API path."""
    assert cp._notion_id("0" * 32) == "0" * 32
    with pytest.raises(RuntimeError):
        cp._notion_id("../users")


@pytest.mark.parametrize(
    ("text", "want"),
    [
        ("saves to /downloads/<filename>", "saves to /downloads/\\<filename>"),
        ("returns {id}", "returns \\{id\\}"),
        ("keeps `<x>` and `{y}` as code", "keeps `<x>` and `{y}` as code"),
        ("already \\<escaped", "already \\<escaped"),
    ],
)
def test_mdx_escape_outside_code_spans(text: str, want: str) -> None:
    """A bare <tag> or {expr} would make MDX fail to parse the changelog."""
    assert cp._mdx_escape(text) == want


def test_gating_flags_finds_classifier_and_neighbor_flags() -> None:
    """An unrolled hinted flag, or a held neighbor's flag, gates an entry."""
    deep = "a/b/c/d/e/f.py"
    prs = {
        1: {"title": "feat: agent archive button", "files": [deep]},
        2: {"title": "feat: agent archive api", "files": [deep]},
        3: {"title": "fix: unrelated", "files": ["x.py"]},
    }
    results = {
        1: {"pass1": {"feature_flag": "fleet_support_archive"}},
        3: {"pass1": {"feature_flag": "shipped_flag"}},
    }
    flags = {
        "fleet_support_archive": {"rolled_out": False},
        "shipped_flag": {"rolled_out": True},
        "held_flag": {"rolled_out": False},
    }
    held = [(2, "held_flag")]
    gates = cp._gating_flags({"prs": [1]}, prs, results, held, flags)
    assert [flag for flag, _ in gates] == ["fleet_support_archive", "held_flag"]
    assert cp._gating_flags({"prs": [3]}, prs, results, held, flags) == []


def test_text_reasons_catch_internal_names_and_flag_keys() -> None:
    """Text problems go to a human; they are separate from gating."""
    flags = {"webhook_unification": {"rolled_out": False}}
    group = {"title": "", "entry": "Behind the webhook_unification_backend flag."}
    assert cp._text_reasons(group, flags) == ["names flag key webhook_unification"]
    group = {"title": "", "entry": "Set it on the host-backend deployment."}
    assert cp._text_reasons(group, flags) == ["internal name: host-backend"]
    assert cp._text_reasons({"title": "T", "entry": "Plain text."}, flags) == []


def test_fix_text_publishes_clean_rewrites_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A clean rewrite publishes; a leaky one goes to a human; a drop is recorded."""
    replies = {
        1: {"action": "rewrite", "title": "", "entry": "Set the token age limit."},
        2: {"action": "rewrite", "title": "", "entry": "Set it on host-backend."},
        3: {"action": "drop", "title": "", "entry": "", "reason": "self-hosted only"},
    }

    def fake_claude(
        _system: str, _schema: dict, prompt: str, _model: str, _workdir: Path
    ) -> tuple[dict, dict]:
        number = int(re.search(r'number="?(\d+)', prompt).group(1))
        return replies[number], {"cost_usd": 0.01}

    monkeypatch.setattr(cp, "_claude", fake_claude)
    monkeypatch.setattr(cp, "_group_prompt", lambda g, _prs: f'number="{g["prs"][0]}"')
    groups = [
        ({"prs": [n], "layer": "change", "title": "", "entry": "x"}, ["internal"])
        for n in (1, 2, 3)
    ]
    fixed, still, dropped, cost = cp._fix_text(groups, {}, {}, tmp_path, 2)
    assert [new["entry"] for _, new in fixed] == ["Set the token age limit."]
    assert still[0][1][-1] == "rewrite still has internal name: host-backend"
    assert dropped[0][1] == "self-hosted only"
    assert cost == pytest.approx(0.03)
