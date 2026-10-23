"""Check egress inventory validation, generated pages, and the public artifact."""

import copy
import json
import shutil
from pathlib import Path

import pytest

from pipeline.core.builder import DocumentationBuilder
from scripts.generate_egress_ip_tables import (
    INVENTORY,
    PAGES,
    ROOT,
    load_inventory,
    render_table,
    update_tables,
)


def test_egress_tables_detect_inventory_drift(tmp_path: Path) -> None:
    """An inventory edit must update both the table and its reserved annotation."""
    for relative_path in [INVENTORY, *PAGES.values()]:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative_path, target)
    update_tables(tmp_path, check=True)
    data = load_inventory(tmp_path / INVENTORY)
    old_version = data["version"]
    data["addresses"][0]["status"] = "reserved"
    (tmp_path / INVENTORY).write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match=r"egress-ip-addresses.json \(version\)"):
        update_tables(tmp_path, check=True)
    update_tables(tmp_path)
    update_tables(tmp_path, check=True)
    assert load_inventory(tmp_path / INVENTORY)["version"] != old_version
    page = tmp_path / PAGES["langsmith"]
    page.write_text(page.read_text().replace("34.59.65.97", "34.59.65.98"))
    with pytest.raises(ValueError, match=r"cloud\.mdx"):
        update_tables(tmp_path, check=True)
    table = render_table(data["addresses"], "langsmith")
    assert "34.59.65.97 (reserved)" in table
    assert "35.197.29.146" not in table


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("cidr", "10.0.0.1/32"),
        ("cidr", "34.59.65.0/24"),
        ("cidr", "34.59.65.97"),
        ("cidr", "2001:4860:4860::8888/128"),
        ("service", "unknown"),
        ("cloud", "azure"),
        ("region", "<script>"),
        ("status", "retired"),
        ("unexpected", "field"),
    ],
)
def test_invalid_egress_addresses_fail(tmp_path: Path, field: str, value: str) -> None:
    """Reject invalid or unpublishable entries before generating Markdown."""
    data = load_inventory(ROOT / INVENTORY)
    data["addresses"][0][field] = value
    path = tmp_path / "inventory.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match=r"Expected|Invalid|Each|Exactly"):
        load_inventory(path)


def test_duplicate_egress_address_fails(tmp_path: Path) -> None:
    """Do not publish conflicting statuses for the same address and scope."""
    data = load_inventory(ROOT / INVENTORY)
    duplicate = copy.copy(data["addresses"][0])
    duplicate["status"] = "reserved"
    data["addresses"].append(duplicate)
    path = tmp_path / "inventory.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate address"):
        load_inventory(path)


def test_build_publishes_egress_inventory(tmp_path: Path) -> None:
    """Full builds preserve the JSON bytes at the documented unversioned URL."""
    source = tmp_path / INVENTORY
    source.parent.mkdir(parents=True)
    shutil.copy2(ROOT / INVENTORY, source)
    build = tmp_path / "build"
    DocumentationBuilder(tmp_path / "src", build).build_all()
    artifact = build / "langsmith/egress-ip-addresses.json"
    assert artifact.read_bytes() == source.read_bytes()
    assert list(build.rglob("egress-ip-addresses.json")) == [artifact]
