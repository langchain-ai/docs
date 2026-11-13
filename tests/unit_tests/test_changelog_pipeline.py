"""Tests for scripts/changelog_pipeline.py helpers that need no network or model."""

from __future__ import annotations

import datetime as dt
import json
import re
from io import BytesIO
from types import SimpleNamespace
from typing import TYPE_CHECKING, Never
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from uuid import UUID

import pytest
from cryptography.fernet import Fernet

from scripts import changelog_pipeline as cp

if TYPE_CHECKING:
    from pathlib import Path
    from urllib.request import Request


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
        (
            "````markdown\n```go\nFlag: example\n```\n````\n\nFlag: real_flag",
            ["real_flag"],
        ),
        (
            "```\nFlag: none\n``` not a close\nFlag: example_2\n```\nFlag: real_flag",
            ["real_flag"],
        ),
        ("Flag: real_flag\n```\nFlag: example", ["real_flag"]),
        ("Flag: <!--\n-->none", []),
        ("```Flag: none```\nFlag: real_flag", ["real_flag"]),
        ("Flag: Some_Flag\nFlag: some_flag", ["Some_Flag"]),
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
    """Pending or missing flags stay held; archived or conflicting flags drop."""
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
    assert sorted(kept) == ["3", "4"]
    assert sorted(dropped) == ["2", "5"]
    assert "not found in Datadog" in kept["4"]


def test_released_prs_are_marked_for_grouping_and_writing() -> None:
    """Released PRs carry a marker, so stale "behind a flag" notes do not drop them."""
    pr = {
        "title": "feat: custom views",
        "body": "Behind a flag, default off.",
        "files": ["a.ts"],
        "omitted_files": [],
        "diff": "+x",
    }
    prs = {1: pr, 2: {**pr, "title": "fix: other"}}
    results = {n: {"pass1": {"reason": "flag off", "evidence": []}} for n in prs}
    notes = cp._group_notes([1, 2], prs, results, frozenset({1}))
    assert notes.splitlines()[0].startswith("#1 | [released] feat: custom views")
    assert "[released]" not in notes.splitlines()[1]

    group = {"label": "Custom views", "layer": "highlight", "prs": [1]}
    assert 'released="true"' in cp._group_prompt(group, prs, frozenset({1}))
    assert 'released="true"' not in cp._group_prompt(group, prs)
    assert "[released]" in cp.GROUP_SYSTEM
    assert 'released="true"' in cp.ENTRY_SYSTEM
    assert 'released="true"' in cp.HIGHLIGHT_SYSTEM
    assert cp.ROLLOUT_FACT in cp._group_prompt(group, prs, frozenset({1}))
    assert "<rollout>" not in cp._group_prompt(group, prs)


def test_datadog_state_overrides_a_dropped_released_group() -> None:
    """A released PR's group publishes unless an earlier entry announced it."""
    groups = [
        {"prs": [1], "layer": "drop", "announced_before": False},
        {"prs": [2], "layer": "drop", "announced_before": True},
        {"prs": [3], "layer": "drop", "announced_before": False},
        {"prs": [4, 5], "layer": "drop"},
        {"prs": [6], "layer": "highlight", "announced_before": False},
    ]
    assert cp._keep_released(groups, frozenset({1, 2, 5, 6})) == 2
    assert [g["layer"] for g in groups] == [
        "change",  # released, not announced: Datadog wins over the stale notes
        "drop",  # released, but last week's entry already announced it
        "drop",  # not released: the model's drop stands
        "change",  # one released PR is enough; a missing field means not announced
        "highlight",  # not dropped: unchanged
    ]
    # Declared and required: the name appears once in properties, once in required.
    assert json.dumps(cp.GROUP_SCHEMA).count('"announced_before"') == 2


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


@pytest.mark.parametrize(
    ("entry", "leak"),
    [
        ("Run `langdev rr stackup` to start it.", "langdev"),
        ("Log in with no Supabase sign-in screen.", "Supabase"),
        ("Available on staging and US prod control planes.", "prod control planes"),
    ],
)
def test_text_reasons_catch_internal_tooling_and_environments(
    entry: str, leak: str
) -> None:
    """LangChain's own dev tooling and environments never reach the changelog."""
    group = {"title": "", "entry": entry}
    assert cp._text_reasons(group, {}) == [f"internal name: {leak}"]


@pytest.mark.parametrize(
    ("entry", "leak"),
    [
        ("Pass `enableColumnReordering: false` to `useDataGrid`.", "useDataGrid"),
        ("DataGridV2 column headers can now be dragged.", "DataGridV2"),
        ("Approval runs on each reconciler tick.", "reconciler"),
        ("It can no longer crowd out other customers.", "other customers"),
    ],
)
def test_text_reasons_catch_frontend_code_and_hosting_internals(
    entry: str, leak: str
) -> None:
    """Component names and how Cloud is run never reach the Cloud changelog."""
    group = {"title": "", "entry": entry}
    assert cp._text_reasons(group, {}) == [f"internal name: {leak}"]


@pytest.mark.parametrize(
    "entry",
    [
        "Users and useful defaults stay the same.",
        "Call `/v2/runs/analytics` with OpenAI or GPT-6.",
    ],
)
def test_component_re_skips_ordinary_words_and_versioned_routes(entry: str) -> None:
    """The case-sensitive patterns leave plain words and API routes alone."""
    assert cp._text_reasons({"title": "", "entry": entry}, {}) == []


def test_latest_bullets_skips_the_week_being_written(tmp_path: Path) -> None:
    """A rerun after the new week is inserted still compares against last week."""
    changelog = tmp_path / "changelog.mdx"
    changelog.write_text(
        '<Update label="Oct 19-26">\n- This week.\n</Update>\n'
        '<Update label="Oct 12-19">\n- Last week.\n</Update>\n'
        '<Update label="Oct 5-12">\n- Older.\n</Update>\n'
    )
    assert cp._latest_bullets(changelog, skip="Oct 19-26") == ["Last week."]
    assert cp._latest_bullets(changelog, skip="Oct 26-Nov 2") == ["This week."]


def test_rollout_reasons_flag_partial_availability() -> None:
    """An entry for some workspaces only is left out, never rewritten to sound GA."""
    group = {"title": "", "entry": "It runs for workspaces in a limited rollout."}
    assert cp._rollout_reasons(group) == ["partial rollout: limited rollout"]
    group = {"title": "", "entry": "This behavior is off by default until enabled."}
    assert cp._rollout_reasons(group) == ["partial rollout: off by default until"]
    group = {"title": "", "entry": "Wrapping is off by default."}
    assert cp._rollout_reasons(group) == []


def test_preflight_model_stops_on_a_rejected_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A rejected key stops the run before collection, not once per PR."""

    def reject(*_: object) -> None:
        msg = "Error code: 401 - invalid x-api-key"
        raise RuntimeError(msg)

    monkeypatch.setenv("ANTHROPIC_API_KEY", "bad")
    monkeypatch.setattr(cp, "_claude_api", reject)
    with pytest.raises(SystemExit, match="invalid x-api-key"):
        cp._preflight_model()


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
        match = re.search(r'number="?(\d+)', prompt)
        assert match is not None
        number = int(match.group(1))
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


def _datadog_flag(**environment: object) -> dict:
    return {
        "value_type": "BOOLEAN",
        "variants": [{"id": "on", "value": "true"}, {"id": "off", "value": "false"}],
        "feature_flag_environments": [
            {
                "environment_id": "prod",
                "status": "ENABLED",
                "default_variant_id": "on",
                "allocations": None,
                **environment,
            }
        ],
    }


def _allocation(variant: str = "on", **fields: object) -> dict:
    return {
        "order_position": 0,
        "type": "FEATURE_GATE",
        "targeting_rules": [],
        "variant_weights": [{"variant_id": variant, "value": 100}],
        **fields,
    }


@pytest.mark.parametrize(
    ("environment", "expected"),
    [
        ({}, True),
        ({"status": "DISABLED"}, False),
        ({"status": "UNKNOWN"}, False),
        ({"default_variant_id": "off"}, False),
        ({"default_variant_id": "missing"}, False),
        ({"override_variant_id": "off"}, False),
        ({"default_variant_id": "off", "override_variant_id": "on"}, True),
        ({"default_variant_id": "off", "allocations": [_allocation()]}, True),
        ({"allocations": [_allocation("off")]}, False),
        (
            {
                "allocations": [
                    _allocation(
                        targeting_rules=[
                            {
                                "conditions": [
                                    {
                                        "attribute": "tier",
                                        "operator": "ONE_OF",
                                        "value": ["preview"],
                                    }
                                ]
                            }
                        ]
                    )
                ]
            },
            True,
        ),
        (
            {
                "default_variant_id": "off",
                "allocations": [
                    _allocation(
                        targeting_rules=[
                            {
                                "conditions": [
                                    {
                                        "attribute": "tier",
                                        "operator": "ONE_OF",
                                        "value": ["preview"],
                                    }
                                ]
                            }
                        ]
                    )
                ],
            },
            False,
        ),
        (
            {
                "allocations": [
                    _allocation(
                        "off",
                        targeting_rules=[
                            {
                                "conditions": [
                                    {
                                        "attribute": "tier",
                                        "operator": "ONE_OF",
                                        "value": ["preview"],
                                    }
                                ]
                            }
                        ],
                    )
                ]
            },
            False,
        ),
        (
            {
                "allocations": [
                    _allocation(
                        variant_weights=[
                            {"variant_id": "on", "value": 50},
                            {"variant_id": "off", "value": 50},
                        ]
                    )
                ]
            },
            False,
        ),
        (
            {
                "allocations": [
                    _allocation(variant_weights=[{"variant_id": "on", "value": 50}])
                ]
            },
            False,
        ),
        ({"allocations": [_allocation(variant_weights=[])]}, False),
        ({"allocations": [_allocation(experiment_id="experiment")]}, False),
        (
            {
                "allocations": [
                    _allocation(
                        exposure_schedule={"rollout_steps": [{"exposure_ratio": 1}]}
                    )
                ]
            },
            False,
        ),
        ({"allocations": [_allocation(status="draft")]}, False),
        ({"allocations": [_allocation(type="UNKNOWN")]}, False),
        ({"allocations": {}}, False),
        ({"allocations": [_allocation(order_position=None)]}, False),
    ],
)
def test_is_fully_rolled_out(environment: dict, expected: bool) -> None:
    """Enabled is insufficient: every reachable audience must receive the on value."""
    assert cp.is_fully_rolled_out(_datadog_flag(**environment), {"prod"}) is expected


def test_rollout_requires_complete_production_details() -> None:
    """Every production environment must be present and rolled out."""
    flag = _datadog_flag()
    assert not cp.is_fully_rolled_out(flag, set())
    assert not cp.is_fully_rolled_out(flag, {"prod", "other-prod"})
    other = {**flag["feature_flag_environments"][0], "environment_id": "other-prod"}
    flag["feature_flag_environments"].append(other)
    assert cp.is_fully_rolled_out(flag, {"prod", "other-prod"})
    other["default_variant_id"] = "off"
    assert not cp.is_fully_rolled_out(flag, {"prod", "other-prod"})
    flag["archived_at"] = "2026-01-01T00:00:00Z"
    assert not cp.is_fully_rolled_out(flag, {"prod"})
    del flag["archived_at"]
    del flag["feature_flag_environments"][0]["allocations"]
    assert not cp.is_fully_rolled_out(flag, {"prod"})


def test_rollout_honors_rule_order_and_targeted_exceptions() -> None:
    """A reachable exception blocks rollout; rules after a catch-all cannot."""
    catchall = _allocation(order_position=1)
    exception = _allocation(
        "off",
        order_position=0,
        targeting_rules=[
            {
                "conditions": [
                    {"attribute": "tier", "operator": "ONE_OF", "value": ["preview"]}
                ]
            }
        ],
    )
    flag = _datadog_flag(default_variant_id="off", allocations=[catchall, exception])
    assert not cp.is_fully_rolled_out(flag, {"prod"})
    exception["order_position"] = 2
    assert cp.is_fully_rolled_out(flag, {"prod"})


def test_non_boolean_rollout_requires_one_known_variant() -> None:
    """Uniform non-boolean values retain the existing release behavior."""
    flag = _datadog_flag()
    flag["value_type"] = "STRING"
    flag["variants"] = [{"id": "on", "value": "general"}]
    assert cp.is_fully_rolled_out(flag, {"prod"})
    flag["variants"] = []
    assert not cp.is_fully_rolled_out(flag, {"prod"})


def test_datadog_inventory_paginates_and_fetches_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """List payloads omit allocations; rollout must use each detail response."""
    monkeypatch.setenv("DD_API_KEY", "test-api")
    monkeypatch.setenv("DD_APP_KEY", "test-app")
    flags = [
        {"id": str(UUID(int=i + 1)), "attributes": {"key": f"flag-{i}"}}
        for i in range(51)
    ]
    detail_reads = []

    def get(path: str, headers: dict) -> dict:
        assert headers == {"DD-API-KEY": "test-api", "DD-APPLICATION-KEY": "test-app"}
        url = urlsplit(path)
        offset = int(parse_qs(url.query).get("offset", [0])[0])
        if url.path.endswith("/environments"):
            return {
                "data": []
                if offset
                else [
                    {"id": "prod", "attributes": {"is_production": True}},
                    {"id": "dev", "attributes": {"is_production": False}},
                ]
            }
        if url.path == "/api/v2/feature-flags":
            return {
                "data": flags[offset : offset + 50],
                "links": {"next": "https://example.com/never-follow"},
            }
        index = UUID(url.path.rsplit("/", 1)[1]).int - 1
        detail_reads.append(index)
        return {"data": {"attributes": {"key": f"flag-{index}", **_datadog_flag()}}}

    monkeypatch.setattr(cp, "_datadog_get", get)
    index, production = cp.datadog_flag_index()
    assert production == {"prod"}
    assert set(index) == {f"flag-{i}" for i in range(51)}
    assert detail_reads == list(range(51))
    assert cp.is_fully_rolled_out(index["flag-50"], production)


def test_inventory_failure_never_reuses_a_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An API error cannot publish from a previous Eppo or Datadog success."""
    old = {"example": {"rolled_out": True}}
    for provider in ("eppo", "datadog"):
        (tmp_path / f"{provider}-flags.json").write_text(json.dumps(old))

    def unavailable() -> Never:
        url = "https://api.datadoghq.com"
        raise HTTPError(url, 403, "Forbidden", None, None)

    monkeypatch.setattr(cp, "datadog_flag_index", unavailable)
    with pytest.raises(HTTPError):
        cp._load_flags(tmp_path)
    monkeypatch.setattr(
        cp,
        "datadog_flag_index",
        lambda: ({"example": _datadog_flag(default_variant_id="off")}, {"prod"}),
    )
    flags = cp._load_flags(tmp_path)
    assert flags["example"]["rolled_out"] is False
    assert json.loads((tmp_path / "datadog-flags.json").read_text()) == flags


def test_datadog_inventory_rejects_missing_production_and_duplicate_pages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing credentials/configuration or a looping API must stop the run."""
    monkeypatch.setenv("DD_API_KEY", "test-api")
    monkeypatch.setenv("DD_APP_KEY", "test-app")
    monkeypatch.setattr(cp, "_datadog_get", lambda *_: {"data": []})
    with pytest.raises(ValueError, match="No Datadog production"):
        cp.datadog_flag_index()
    monkeypatch.setattr(cp, "_datadog_get", lambda *_: {"data": [{"id": "same"}]})
    with pytest.raises(ValueError, match="duplicate"):
        list(cp._datadog_resources("/api/v2/feature-flags", {}))
    monkeypatch.delenv("DD_APP_KEY")
    with pytest.raises(SystemExit, match="DD_APP_KEY"):
        cp.datadog_flag_index()


def test_datadog_http_uses_site_and_rejects_redirects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Credentials go only to the selected, allowlisted Datadog site."""
    monkeypatch.setenv("DD_SITE", "us5.datadoghq.com")

    def opener(handler: cp._NoDatadogRedirect) -> SimpleNamespace:
        # urllib calls this before issuing a redirected authenticated request.
        with pytest.raises(ValueError, match="redirects"):
            handler.redirect_request(
                None, None, 302, "Found", {}, "https://example.com"
            )

        def request(req: Request, timeout: int) -> BytesIO:
            assert req.full_url == "https://api.us5.datadoghq.com/api/v2/feature-flags"
            assert req.get_header("Dd-api-key") == "test-api"
            assert timeout == 15
            return BytesIO(b'{"data": []}')

        return SimpleNamespace(open=request)

    monkeypatch.setattr(cp.urllib.request, "build_opener", opener)
    assert cp._datadog_get("/api/v2/feature-flags", {"DD-API-KEY": "test-api"}) == {
        "data": []
    }
    monkeypatch.setenv("DD_SITE", "datadoghq.com@example.com")
    with pytest.raises(ValueError, match="allowlist"):
        cp._datadog_get("/api/v2/feature-flags", {})


def test_mock_preserves_new_missing_flags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A declared flag absent from Datadog can release in a later week."""
    for directory in ("prs", "results"):
        (tmp_path / directory).mkdir()
    (tmp_path / "prs/1.json").write_text(
        json.dumps(
            {
                "title": "feat: example",
                "body": "Flag: example",
                "merged_at": "2026-01-06",
            }
        )
    )
    (tmp_path / "results/1.json").write_text(
        json.dumps({"pass1": {"tier": "announce"}})
    )
    (tmp_path / "datadog-flags.json").write_text("{}")
    monkeypatch.setattr(cp, "_claude", lambda *_: ({"groups": []}, {}))
    monkeypatch.setattr(cp, "_docs_pages", dict)
    monkeypatch.setattr(cp, "_beta_features", list)
    monkeypatch.setattr(cp, "_latest_bullets", lambda *_, **__: [])
    cp.cmd_mock(
        SimpleNamespace(
            out=str(tmp_path),
            results="results",
            since="2026-01-05",
            until="2026-01-12",
            label=None,
            workers=1,
        )
    )
    output = tmp_path / "mock-2026-01-05"
    held = json.loads((output / "held.json").read_text())
    assert held["1"]["flag"] == "example"
    assert not (output / "mock.mdx").read_text().strip()
    released, kept, dropped = cp._release_held(held, {"example": {"rolled_out": True}})
    assert list(released) == ["1"]
    assert not kept
    assert not dropped
