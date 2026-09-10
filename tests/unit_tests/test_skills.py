"""Tests for the agent skills in `.agents/skills/`.

These are structural checks only. They verify that every skill parses, that its
frontmatter is well formed, and that the repository paths and make targets a
skill tells an agent to use still exist. A skill that points at a renamed target
is worse than no skill, because the agent follows it confidently.
"""

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"

# Existence is only checked under roots that are tracked in git. Paths under
# gitignored roots (`.claude/`, `.bin/`, `build/`) are absent in a fresh clone.
CHECKED_ROOTS = (
    "src/",
    "scripts/",
    "pipeline/",
    "tests/",
    ".github/",
    ".agents/",
    ".deepagents/",
)
CHECKED_FILES = frozenset(
    {"AGENTS.md", "CLAUDE.md", "IDE_SETUP.md", "Makefile", ".vale.ini", ".cursorrules"}
)

# Illustrative paths that stand in for a real one and are not expected to exist.
PLACEHOLDER = re.compile(r"path/to|<[^>]+>|(example|old-name|new-name)\.mdx$")

# A backticked token that looks like a repository path.
PATH_TOKEN = re.compile(
    r"`([^`\s]+/[^`\s]*|[A-Za-z0-9_.-]+\.(?:md|mdx|json|ini|py|yml))`"
)

MAKE_TARGET = re.compile(r"`?make ([a-z][a-z0-9_-]*)")

# Frontmatter keys the Agent Skills spec and the Claude Code extensions accept.
# A key outside this set is almost always a typo, such as `allowed_tools`.
KNOWN_KEYS = frozenset(
    {
        "agent",
        "allowed-tools",
        "argument-hint",
        "arguments",
        "background",
        "compatibility",
        "context",
        "description",
        "disable-model-invocation",
        "disallowed-tools",
        "effort",
        "hooks",
        "license",
        "metadata",
        "model",
        "name",
        "paths",
        "shell",
        "user-invocable",
        "when_to_use",
    }
)


def skill_dirs() -> list[Path]:
    """Every skill directory in the tree."""
    return sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())


def frontmatter(skill_md: Path) -> dict:
    """Parse the YAML frontmatter block of a SKILL.md."""
    text = skill_md.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{skill_md} has no frontmatter block"
    _, block, _ = text.split("---\n", 2)
    return yaml.safe_load(block)


def make_targets() -> set[str]:
    """Every target defined in the root Makefile."""
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    return set(re.findall(r"^([a-z][a-z0-9_-]*):", makefile, flags=re.MULTILINE))


def test_skills_directory_exists() -> None:
    """The canonical skills tree is present."""
    assert SKILLS_DIR.is_dir()
    assert skill_dirs(), "no skills found in .agents/skills/"


@pytest.mark.parametrize("skill_dir", skill_dirs(), ids=lambda p: p.name)
def test_skill_has_valid_frontmatter(skill_dir: Path) -> None:
    """Each skill has a SKILL.md whose name matches its directory."""
    skill_md = skill_dir / "SKILL.md"
    assert skill_md.is_file(), f"{skill_dir} has no SKILL.md"

    meta = frontmatter(skill_md)
    assert meta.get("name") == skill_dir.name, (
        f"{skill_md}: frontmatter name {meta.get('name')!r} "
        f"does not match directory {skill_dir.name!r}"
    )
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", skill_dir.name), (
        f"{skill_dir.name} is not kebab-case"
    )

    description = meta.get("description", "")
    assert description, f"{skill_md}: description is required for discovery"
    assert len(description) <= 1024, (
        f"{skill_md}: description is {len(description)} characters; keep it under 1024"
    )

    unknown = sorted(set(meta) - KNOWN_KEYS)
    assert not unknown, f"{skill_md}: unrecognized frontmatter keys: {unknown}"


@pytest.mark.parametrize("skill_dir", skill_dirs(), ids=lambda p: p.name)
def test_skill_paths_exist(skill_dir: Path) -> None:
    """Repository paths a skill names still exist."""
    skill_md = skill_dir / "SKILL.md"
    missing = []

    for raw in PATH_TOKEN.findall(skill_md.read_text(encoding="utf-8")):
        token = raw.rstrip(",.")
        if "*" in token or "$" in token or token.startswith("~"):
            continue
        if PLACEHOLDER.search(token):
            continue
        if not (token.startswith(CHECKED_ROOTS) or token in CHECKED_FILES):
            continue
        if not (REPO_ROOT / token.rstrip("/")).exists():
            missing.append(token)

    assert not missing, f"{skill_md} names paths that do not exist: {missing}"


@pytest.mark.parametrize("skill_dir", skill_dirs(), ids=lambda p: p.name)
def test_skill_make_targets_exist(skill_dir: Path) -> None:
    """Make targets a skill tells an agent to run still exist."""
    skill_md = skill_dir / "SKILL.md"
    defined = make_targets()
    referenced = set(MAKE_TARGET.findall(skill_md.read_text(encoding="utf-8")))
    missing = sorted(referenced - defined)
    assert not missing, f"{skill_md} names make targets that do not exist: {missing}"


def test_readme_lists_every_skill() -> None:
    """The skills README table stays in step with the tree."""
    readme = (SKILLS_DIR / "README.md").read_text(encoding="utf-8")
    listed = set(re.findall(r"^\| `([a-z0-9-]+)` \|", readme, flags=re.MULTILINE))
    present = {p.name for p in skill_dirs()}
    assert listed == present, (
        f"README table and tree disagree. "
        f"Only in README: {sorted(listed - present)}. "
        f"Only in tree: {sorted(present - listed)}."
    )


def test_agents_md_lists_every_skill() -> None:
    """The Skills section of AGENTS.md stays in step with the tree."""
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    section = agents.split("## Skills", 1)[1].split("## Project structure", 1)[0]
    listed = set(re.findall(r"^\| `([a-z0-9-]+)` \|", section, flags=re.MULTILINE))
    present = {p.name for p in skill_dirs()}
    assert listed == present, (
        f"AGENTS.md Skills table and tree disagree. "
        f"Only in AGENTS.md: {sorted(listed - present)}. "
        f"Only in tree: {sorted(present - listed)}."
    )
