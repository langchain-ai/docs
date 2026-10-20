"""Tests for scripts/check_integration_repos.py."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts import check_integration_repos as cir


class FakeResponse:
    """Minimal response object for stubbed HTTP GETs."""

    def __init__(self, status_code: int, payload: Any = None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self) -> Any:
        return self._payload


def make_get(mapping: dict[str, FakeResponse]):
    """Return a get() that serves ``mapping`` by exact URL."""

    def _get(url: str) -> FakeResponse:
        if url in mapping:
            return mapping[url]
        raise AssertionError(f"unexpected URL: {url}")

    return _get


def test_extract_github_and_gitlab() -> None:
    """Parse GitHub slugs and GitLab project URLs."""
    assert cir.extract_github_repo("acme/langchain-acme") == "acme/langchain-acme"
    assert (
        cir.extract_github_repo("https://github.com/acme/langchain-acme/tree/main")
        == "acme/langchain-acme"
    )
    assert (
        cir.extract_gitlab_url(
            "https://gitlab.com/bitkaio/langchain/kubernetes-sandbox"
        )
        == "https://gitlab.com/bitkaio/langchain/kubernetes-sandbox"
    )


def test_classify_skips_first_party() -> None:
    """First-party langchain-ai packages are never delisted by this checker."""
    finding = cir.classify_package(
        {"name": "langchain-openai", "repo": "langchain-ai/langchain"},
        docs_urls_by_package={},
        get=make_get({}),
    )
    assert finding.disposition == "skip_first_party"


def test_classify_fix_from_pypi_github() -> None:
    """A 404 packages.yml repo is fixed when PyPI lists a live GitHub URL."""
    get = make_get(
        {
            "https://github.com/old-owner/langchain-acme": FakeResponse(404),
            "https://pypi.org/pypi/langchain-acme/json": FakeResponse(
                200,
                {
                    "info": {
                        "project_urls": {
                            "Source": "https://github.com/new-owner/langchain-acme"
                        }
                    }
                },
            ),
            "https://github.com/new-owner/langchain-acme": FakeResponse(200),
        }
    )
    finding = cir.classify_package(
        {"name": "langchain-acme", "repo": "old-owner/langchain-acme"},
        docs_urls_by_package={},
        get=get,
    )
    assert finding.disposition == "fix"
    assert finding.new_repo == "new-owner/langchain-acme"


def test_classify_attention_when_gitlab_docs_live() -> None:
    """Do not delist when a live GitLab docs_url remains."""
    get = make_get(
        {
            "https://github.com/bitkaio/kubernetes-sandbox": FakeResponse(404),
            "https://pypi.org/pypi/langchain-kubernetes/json": FakeResponse(
                200, {"info": {"project_urls": {}}}
            ),
            "https://registry.npmjs.org/@bitkaio%2Flangchain-kubernetes": FakeResponse(
                200, {"repository": {}}
            ),
            "https://gitlab.com/bitkaio/langchain/kubernetes-sandbox": FakeResponse(
                200
            ),
        }
    )
    finding = cir.classify_package(
        {
            "name": "langchain-kubernetes",
            "repo": "bitkaio/kubernetes-sandbox",
            "js": "@bitkaio/langchain-kubernetes",
        },
        docs_urls_by_package={
            "langchain-kubernetes": [
                "https://gitlab.com/bitkaio/langchain/kubernetes-sandbox"
            ]
        },
        get=get,
    )
    assert finding.disposition == "attention"
    assert "GitLab" in finding.detail


def test_classify_delist_when_only_marketing_docs_remain() -> None:
    """Marketing docs URLs do not count as a VCS home and do not block delist."""
    get = make_get(
        {
            "https://github.com/Hashlock-Tech/langchain-hashlock": FakeResponse(404),
            "https://pypi.org/pypi/langchain-hashlock/json": FakeResponse(
                200,
                {
                    "info": {
                        "project_urls": {
                            "Documentation": "https://hashlock.markets/docs",
                            "Source": "https://github.com/Hashlock-Tech/langchain-hashlock",
                        }
                    }
                },
            ),
        }
    )
    finding = cir.classify_package(
        {"name": "langchain-hashlock", "repo": "Hashlock-Tech/langchain-hashlock"},
        docs_urls_by_package={
            "langchain-hashlock": ["https://hashlock.markets/docs"]
        },
        get=get,
    )
    assert finding.disposition == "delist"


def test_classify_attention_for_first_party_alternate() -> None:
    """Do not auto-adopt a langchain-ai monorepo URL from PyPI."""
    get = make_get(
        {
            "https://github.com/topoteretes/langchain-cognee": FakeResponse(404),
            "https://pypi.org/pypi/langchain-cognee/json": FakeResponse(
                200,
                {
                    "info": {
                        "project_urls": {
                            "Homepage": "https://github.com/langchain-ai/langchain"
                        }
                    }
                },
            ),
            "https://github.com/langchain-ai/langchain": FakeResponse(200),
        }
    )
    finding = cir.classify_package(
        {"name": "langchain-cognee", "repo": "topoteretes/langchain-cognee"},
        docs_urls_by_package={},
        get=get,
    )
    assert finding.disposition == "attention"
    assert "first-party" in finding.detail


def test_classify_fix_double_slash_typo() -> None:
    """Normalize owner//repo typos when the cleaned slug is live."""
    get = make_get(
        {
            "https://github.com/ContextualAI/langchain-contextual": FakeResponse(200),
        }
    )
    finding = cir.classify_package(
        {"name": "langchain-contextual", "repo": "ContextualAI//langchain-contextual"},
        docs_urls_by_package={},
        get=get,
    )
    assert finding.disposition == "fix"
    assert finding.new_repo == "ContextualAI/langchain-contextual"


def test_classify_delist_when_no_alternate() -> None:
    """Delist when GitHub is gone and registries have no live VCS home."""
    get = make_get(
        {
            "https://github.com/dead-org/langchain-dead": FakeResponse(404),
            "https://pypi.org/pypi/langchain-dead/json": FakeResponse(
                200,
                {
                    "info": {
                        "project_urls": {
                            "Source": "https://github.com/dead-org/langchain-dead"
                        }
                    }
                },
            ),
        }
    )
    finding = cir.classify_package(
        {"name": "langchain-dead", "repo": "dead-org/langchain-dead"},
        docs_urls_by_package={
            "langchain-dead": ["https://github.com/dead-org/langchain-dead"]
        },
        get=get,
    )
    assert finding.disposition == "delist"


def test_apply_changes_delists_listings(tmp_path: Path) -> None:
    """--write removes packages.yml, external YAML, downloads row, and card."""
    repo = tmp_path
    (repo / "scripts" / "data").mkdir(parents=True)
    (repo / "src" / "oss" / "python" / "integrations" / "providers").mkdir(
        parents=True
    )
    (repo / "src" / "snippets" / "oss").mkdir(parents=True)

    (repo / "packages.yml").write_text(
        "packages:\n"
        "- name: langchain-dead\n"
        "  repo: dead-org/langchain-dead\n"
        "  downloads: 1\n"
        "- name: langchain-alive\n"
        "  repo: alive-org/langchain-alive\n"
        "  downloads: 2\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "data" / "integration_external_docs.yaml").write_text(
        "python:\n"
        "  tools:\n"
        "  - name: DeadToolkit\n"
        "    pypi: langchain-dead\n"
        "    docs_url: https://github.com/dead-org/langchain-dead\n"
        "  - name: AliveToolkit\n"
        "    pypi: langchain-alive\n"
        "    docs_url: https://alive.example/docs\n",
        encoding="utf-8",
    )
    providers = repo / "src/oss/python/integrations/providers/all_providers.mdx"
    providers.write_text(
        "<CardGroup cols={3}>\n"
        "\n"
        "    <Card\n"
        '        title="Dead"\n'
        '        href="https://github.com/dead-org/langchain-dead"\n'
        '        icon="link"\n'
        "    >\n"
        "        Gone.\n"
        "    </Card>\n"
        "\n"
        "    <Card\n"
        '        title="Alive"\n'
        '        href="https://alive.example/docs"\n'
        '        icon="link"\n'
        "    >\n"
        "        Still here.\n"
        "    </Card>\n"
        "\n"
        "</CardGroup>\n",
        encoding="utf-8",
    )
    downloads = repo / "src/snippets/oss/python-tools-downloads.mdx"
    downloads.write_text(
        "| Name | Downloads |\n"
        "| --- | --- |\n"
        "| [`DeadToolkit`](https://github.com/dead-org/langchain-dead) | "
        '<span data-sort-value="1"><a href="https://pypi.org/project/langchain-dead/"'
        ' target="_blank">badge</a></span> |\n'
        "| [`AliveToolkit`](https://alive.example/docs) | "
        '<span data-sort-value="2"><a href="https://pypi.org/project/langchain-alive/"'
        ' target="_blank">badge</a></span> |\n',
        encoding="utf-8",
    )

    finding = cir.PackageFinding(
        name="langchain-dead",
        repo="dead-org/langchain-dead",
        disposition="delist",
        detail="gone",
        pypi="langchain-dead",
        removed_docs_urls=["https://github.com/dead-org/langchain-dead"],
    )
    summary = cir.apply_changes(repo_root=repo, findings=[finding], write=True)

    packages = (repo / "packages.yml").read_text(encoding="utf-8")
    assert "langchain-dead" not in packages
    assert "langchain-alive" in packages

    external = (repo / "scripts/data/integration_external_docs.yaml").read_text(
        encoding="utf-8"
    )
    assert "DeadToolkit" not in external
    assert "AliveToolkit" in external

    providers_text = providers.read_text(encoding="utf-8")
    assert 'title="Dead"' not in providers_text
    assert 'title="Alive"' in providers_text

    downloads_text = downloads.read_text(encoding="utf-8")
    assert "langchain-dead" not in downloads_text
    assert "langchain-alive" in downloads_text

    assert "langchain-dead" in summary["delisted"]
    assert "Dead" in summary["cards_removed"]


def test_provider_card_kept_when_sibling_package_remains() -> None:
    """Keep the provider card when another package still uses the provider key."""
    text = (
        "\n    <Card\n"
        '        title="Dead"\n'
        '        href="https://github.com/dead-org/langchain-dead"\n'
        '        icon="link"\n'
        "    >\n"
        "        Shared provider.\n"
        "    </Card>\n"
    )
    finding = cir.PackageFinding(
        name="langchain-dead",
        repo="dead-org/langchain-dead",
        disposition="delist",
        detail="gone",
        removed_docs_urls=["https://github.com/dead-org/langchain-dead"],
    )
    updated, removed = cir.remove_provider_cards(
        text,
        delisted=[finding],
        remaining_provider_keys={"dead"},
    )
    assert removed == []
    assert 'title="Dead"' in updated


def test_render_evidence_includes_sections() -> None:
    """Evidence markdown lists fix, delist, and attention rows."""
    md = cir.render_evidence(
        [
            cir.PackageFinding(
                "langchain-a",
                "old/a",
                "fix",
                "moved",
                new_repo="new/a",
            ),
            cir.PackageFinding("langchain-b", "gone/b", "delist", "no vcs"),
            cir.PackageFinding(
                "langchain-c",
                "gone/c",
                "attention",
                "live gitlab at https://gitlab.com/c/c",
            ),
        ]
    )
    assert "Repo renames applied" in md
    assert "Full delist" in md
    assert "Needs attention" in md
    assert "`langchain-a`" in md
