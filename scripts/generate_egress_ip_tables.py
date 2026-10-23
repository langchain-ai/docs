"""Generate the egress tables from the public IP inventory.

Run with --check in CI; omit --check to update both source pages.
"""

import argparse
import hashlib
import ipaddress
import json
from itertools import zip_longest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = Path("src/langsmith/egress-ip-addresses.json")
PAGES = {
    "langsmith": Path("src/langsmith/cloud.mdx"),
    "langsmith-deployment": Path("src/langsmith/cloud-platform-features.mdx"),
}
START = "{/* BEGIN GENERATED EGRESS IP ADDRESSES */}"
END = "{/* END GENERATED EGRESS IP ADDRESSES */}"


def load_inventory(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"schema_version", "version", "addresses"}:
        raise ValueError("Inventory must contain schema_version, version, and addresses")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("Unsupported schema_version; expected 1")
    if not isinstance(data["version"], str) or not data["version"].strip():
        raise ValueError("Inventory version must be a nonempty string")
    if not isinstance(data["addresses"], list) or not data["addresses"]:
        raise ValueError("Inventory addresses must be a nonempty array")
    seen = set()
    for entry in data["addresses"]:
        if not isinstance(entry, dict) or set(entry) != {
            "service", "cloud", "region", "cidr", "status"
        }:
            raise ValueError("Each address must contain service, cloud, region, cidr, status")
        for key, allowed in {
            "service": PAGES,
            "cloud": ("gcp", "aws"),
            "region": ("us", "eu", "apac"),
            "status": ("active", "reserved"),
        }.items():
            if not isinstance(entry[key], str) or entry[key] not in allowed:
                raise ValueError(f"Invalid {key}: {entry[key]!r}")
        if not isinstance(entry["cidr"], str):
            raise ValueError("cidr must be an IPv4 /32 string")
        network = ipaddress.IPv4Network(entry["cidr"], strict=True)
        if network.prefixlen != 32 or str(network) != entry["cidr"] or not network.is_global:
            raise ValueError(f"Expected a public IPv4 /32: {entry['cidr']!r}")
        identity = tuple(entry[key] for key in ("service", "cloud", "region", "cidr"))
        if identity in seen:
            raise ValueError(f"Duplicate address: {identity}")
        seen.add(identity)
    return data


def render_table(addresses, service):
    columns = {}
    for cloud in ("gcp", "aws"):
        for region in ("us", "eu", "apac"):
            values = [
                entry["cidr"].removesuffix("/32")
                + (" (reserved)" if entry["status"] == "reserved" else "")
                for entry in addresses
                if (entry["service"], entry["cloud"], entry["region"])
                == (service, cloud, region)
            ]
            if values:
                columns[f"{cloud.upper()} {region.upper()}"] = values
    if not columns:
        raise ValueError(f"No addresses for {service}")
    rows = [list(columns), ["---"] * len(columns)]
    rows.extend(zip_longest(*columns.values(), fillvalue=""))
    return "\n".join("| " + " | ".join(row) + " |" for row in rows)


def update_tables(root, *, check=False):
    data = load_inventory(root / INVENTORY)
    stale = []
    canonical = json.dumps(data["addresses"], sort_keys=True, separators=(",", ":"))
    version = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if data["version"] != version:
        stale.append(f"{INVENTORY} (version)")
        if not check:
            data["version"] = version
            (root / INVENTORY).write_text(
                json.dumps(data, indent=2) + "\n", encoding="utf-8"
            )
    for service, relative_path in PAGES.items():
        path = root / relative_path
        content = path.read_text(encoding="utf-8")
        if content.count(START) != 1 or content.count(END) != 1:
            raise ValueError(f"Expected exactly one generated block in {relative_path}")
        before, rest = content.split(START)
        _, after = rest.split(END)
        table = render_table(data["addresses"], service)
        expected = f"{before}{START}\n\n{table}\n\n{END}{after}"
        if expected != content:
            stale.append(str(relative_path))
            if not check:
                path.write_text(expected, encoding="utf-8")
    if check and stale:
        raise ValueError(
            "Egress inventory or tables differ from generated output: " + ", ".join(stale)
            + ". Run python scripts/generate_egress_ip_tables.py"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if a table is stale")
    args = parser.parse_args()
    try:
        update_tables(ROOT, check=args.check)
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
