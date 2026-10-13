"""Tests for scripts/changelog_pipeline.py helpers that need no network or model."""

from __future__ import annotations

import datetime as dt
import json
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


def test_claude_api_parses_structured_output_and_prices_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The API path sends a closed schema, caches the prompt, and prices usage."""
    calls = {}

    class FakeMessages:
        def create(self, **kwargs: object) -> SimpleNamespace:
            calls.update(kwargs)
            return SimpleNamespace(
                stop_reason="end_turn",
                content=[
                    SimpleNamespace(type="text", text=json.dumps({"tier": "announce"}))
                ],
                usage=SimpleNamespace(
                    input_tokens=1_000_000,
                    output_tokens=1_000_000,
                    cache_creation_input_tokens=0,
                    cache_read_input_tokens=1_000_000,
                ),
            )

    monkeypatch.setattr(cp, "_api_client", SimpleNamespace(messages=FakeMessages()))
    out, meta = cp._claude_api(
        "system", {"type": "object", "properties": {}}, "prompt", "haiku"
    )
    assert out == {"tier": "announce"}
    assert calls["model"] == "claude-haiku-5-5"
    assert calls["output_config"]["format"]["schema"]["additionalProperties"] is False
    assert calls["system"][0]["cache_control"] == {"type": "ephemeral"}
    # $0.10 input + $0.50 output + 1M cache reads at a tenth of the input price.
    assert meta["cost_usd"] == pytest.approx(0.10 + 0.50 + 0.01)


def test_claude_api_raises_on_refusal(monkeypatch: pytest.MonkeyPatch) -> None:
    """A refusal is an error, not an empty result."""

    class FakeMessages:
        def create(self, **_: object) -> SimpleNamespace:
            return SimpleNamespace(stop_reason="refusal", content=[], usage=None)

    monkeypatch.setattr(cp, "_api_client", SimpleNamespace(messages=FakeMessages()))
    with pytest.raises(RuntimeError, match="refusal"):
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
    """Merged feat/fix PRs in the window are kept; paging stops past the window."""

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
    first += [pr(100 + i, "docs: x", None, "2026-10-10T00:00:00Z") for i in range(96)]
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
