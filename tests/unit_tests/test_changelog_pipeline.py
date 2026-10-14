"""Tests for scripts/changelog_pipeline.py helpers that need no network or model."""

from __future__ import annotations

import datetime as dt
import json
import re
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest
from cryptography.fernet import Fernet

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
    """Rolled-out flags release; pending flags stay; anything uncertain is dropped."""
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
    released, kept, dropped = cp._release_held(held, flags)
    assert sorted(released) == ["1"]
    assert sorted(kept) == ["3"]
    assert sorted(dropped) == ["2", "4", "5"]
    assert "not found in Eppo" in dropped["4"]


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


def test_render_puts_fixes_under_their_own_heading() -> None:
    """Fixes get a heading, so the collapsed list does not read as the section above."""
    groups = [
        {
            "product": "cloud",
            "layer": "change",
            "section": "Tracing",
            "entry": "c.",
            "rank": 1,
        },
        {"product": "cloud", "layer": "fix", "section": "", "entry": "f.", "rank": 2},
    ]
    block = cp._render("cloud", "October 5-12, 2026", groups, set(), "2026-10-05")
    assert (
        "## Tracing\n\n- c.\n\n## Fixes and improvements\n\n"
        '<Accordion title="Show all fixes">\n\n- f.\n\n</Accordion>'
    ) in block


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


def test_state_files_are_encrypted_and_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A .enc file never holds plaintext, and needs the right key to read."""
    path = tmp_path / "held.json.enc"
    monkeypatch.delenv(cp.STATE_KEY_ENV, raising=False)
    with pytest.raises(SystemExit, match=cp.STATE_KEY_ENV):
        cp._write_state(path, {"1": {"flag": "secret_flag"}})
    assert not path.exists()
    monkeypatch.setenv(cp.STATE_KEY_ENV, Fernet.generate_key().decode())
    cp._write_state(path, {"1": {"flag": "secret_flag"}})
    assert b"secret_flag" not in path.read_bytes()
    assert cp._read_state(path) == {"1": {"flag": "secret_flag"}}
    monkeypatch.setenv(cp.STATE_KEY_ENV, Fernet.generate_key().decode())
    with pytest.raises(SystemExit, match="Cannot decrypt"):
        cp._read_state(path)


def test_held_list_folds_in_and_retires_the_plaintext_copy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The first encrypted write absorbs the old plaintext list and deletes it."""
    monkeypatch.setenv(cp.STATE_KEY_ENV, Fernet.generate_key().decode())
    legacy = tmp_path / ".changelog_held.json"
    legacy.write_text(json.dumps({"9": {"flag": "old"}}))
    path = tmp_path / ".changelog_held.json.enc"
    held = cp._load_held(path)
    assert held == {"9": {"flag": "old"}}
    cp._write_held(path, {**held, "10": {"flag": "new"}})
    assert not legacy.exists()
    assert cp._load_held(path) == {"9": {"flag": "old"}, "10": {"flag": "new"}}
