"""MkDocs Documentation Subset Server.

Create and serve a subset of the Python reference documentation.

Useful for faster development and testing.

Usage:
    python serve_subset.py LangGraph
"""  # noqa: INP001

import argparse
import subprocess
import sys
from collections import deque

import yaml

ALIAS_MAP = {
    "deepagents": "Deep Agents",
    # "core": "langchain-core",
    # "community": "langchain-community",
}
"""Map of alias names to actual section names in the nav.

Canonical section names are the keys defined in the `mkdocs.yml` `nav`.

Allows specifying shorter names when running the script.
"""

# --- Custom YAML handling to preserve tags ---


class EnvTag:
    """Custom YAML tag for environment variables (`!ENV`).

    Preserves `!ENV` tags when reading and writing YAML configurations.

    Args:
        value: The environment variable value or list of values.
    """

    def __init__(self, value: str | list) -> None:
        """Initialize `EnvTag` with a value.

        Args:
            value: The environment variable value or list of values.
        """
        self.value = value

    def __repr__(self) -> str:
        """Return string representation of `EnvTag`."""
        return f"EnvTag({self.value})"


class PythonNameTag:
    """Custom YAML tag for Python name references.

    Preserves `tag:yaml.org,2002:python/name:` tags when reading and writing YAML.

    Args:
        suffix: The suffix part of the Python name tag.
    """

    def __init__(self, suffix: str) -> None:
        """Initialize `PythonNameTag` with a suffix.

        Args:
            suffix: The suffix part of the Python name tag.
        """
        self.suffix = suffix

    def __repr__(self) -> str:
        """Return string representation of `PythonNameTag`."""
        return f"PythonNameTag({self.suffix})"


def env_constructor(loader: yaml.SafeLoader, node: yaml.Node) -> EnvTag:
    """YAML constructor for `!ENV` tags.

    Args:
        loader: YAML loader instance.
        node: YAML node to construct.

    Returns:
        EnvTag: Wrapped environment tag value.
    """
    if isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_scalar(node)
    return EnvTag(value)


def env_representer(dumper: yaml.SafeDumper, data: EnvTag) -> yaml.Node:
    """YAML representer for `EnvTag` objects.

    Args:
        dumper: YAML dumper instance.
        data: `EnvTag` object to represent.

    Returns:
        YAML representation of the environment tag.
    """
    if isinstance(data.value, list):
        return dumper.represent_sequence("!ENV", data.value)
    return dumper.represent_scalar("!ENV", str(data.value))


def python_name_multi_constructor(
    _loader: yaml.SafeLoader, tag_suffix: str, _node: yaml.Node
) -> PythonNameTag:
    """YAML multi-constructor for Python name tags.

    Args:
        _loader: YAML loader instance (unused).
        tag_suffix: The suffix part of the tag.
        _node: YAML node (unused but required by interface).

    Returns:
        PythonNameTag: Wrapped Python name tag.
    """
    return PythonNameTag(tag_suffix)


def python_name_representer(dumper: yaml.SafeDumper, data: PythonNameTag) -> yaml.Node:
    """YAML representer for `PythonNameTag` objects.

    Args:
        dumper: YAML dumper instance.
        data: `PythonNameTag` object to represent.

    Returns:
        YAML representation of the Python name tag.
    """
    return dumper.represent_scalar(f"tag:yaml.org,2002:python/name:{data.suffix}", "")


# Register with SafeLoader
yaml.SafeLoader.add_constructor("!ENV", env_constructor)
yaml.SafeLoader.add_multi_constructor(
    "tag:yaml.org,2002:python/name:", python_name_multi_constructor
)


# Custom Dumper
class CustomDumper(yaml.SafeDumper):
    """Custom YAML dumper that preserves special tags.

    Extends `SafeDumper` to handle `EnvTag` and `PythonNameTag` objects.
    """


CustomDumper.add_representer(EnvTag, env_representer)
CustomDumper.add_representer(PythonNameTag, python_name_representer)

# --- End Custom YAML handling ---


import os

import yaml

# --- Custom YAML handling to preserve tags ---


class EnvTag:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"EnvTag({self.value})"


class PythonNameTag:
    def __init__(self, suffix):
        self.suffix = suffix

    def __repr__(self):
        return f"PythonNameTag({self.suffix})"


def env_constructor(loader, node):
    if isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_scalar(node)
    return EnvTag(value)


def env_representer(dumper, data):
    if isinstance(data.value, list):
        return dumper.represent_sequence("!ENV", data.value)
    return dumper.represent_scalar("!ENV", str(data.value))


def python_name_multi_constructor(loader, tag_suffix, node):
    return PythonNameTag(tag_suffix)


def python_name_representer(dumper, data):
    return dumper.represent_scalar(f"tag:yaml.org,2002:python/name:{data.suffix}", "")


# Register with SafeLoader
yaml.SafeLoader.add_constructor("!ENV", env_constructor)
yaml.SafeLoader.add_multi_constructor(
    "tag:yaml.org,2002:python/name:", python_name_multi_constructor
)


# Custom Dumper
class CustomDumper(yaml.SafeDumper):
    pass


CustomDumper.add_representer(EnvTag, env_representer)
CustomDumper.add_representer(PythonNameTag, python_name_representer)

# --- End Custom YAML handling ---


def find_section(nav: list | dict, target: str) -> dict | None:
    """Search for a section in the nav using BFS."""
    target = target.lower()

    # BFS queue: (nav_item, path_for_debugging)
    queue = deque()

    # Initialize queue with top-level items
    if isinstance(nav, list):
        for item in nav:
            queue.append((item, []))
    else:
        queue.append((nav, []))

    while queue:
        current_nav, path = queue.popleft()

        if isinstance(current_nav, dict):
            key = list(current_nav.keys())[0]
            current_path = path + [key]

            # Check if this key matches our target
            if target == key.lower():
                return current_nav

            # Add children to queue for next level
            child = current_nav[key]
            if isinstance(child, list):
                for child_item in child:
                    queue.append((child_item, current_path))
            elif isinstance(child, dict):
                queue.append((child, current_path))

    return None


def get_all_paths(nav_item: list | dict | str) -> list[str]:
    """Recursively extract all file paths from a nav item."""
    paths = []
    if isinstance(nav_item, list):
        for item in nav_item:
            paths.extend(get_all_paths(item))
    elif isinstance(nav_item, dict):
        for value in nav_item.values():
            paths.extend(get_all_paths(value))
    elif isinstance(nav_item, str):
        paths.append(nav_item)
    return paths


def main():
    parser = argparse.ArgumentParser(description="Serve a subset of the documentation.")
    parser.add_argument(
        "section",
        help="The section of the nav to include (e.g., 'LangGraph', 'Integrations'). Case-insensitive.",
    )
    parser.add_argument(
        "--config", default="mkdocs.yml", help="Path to the input mkdocs.yml file."
    )
    parser.add_argument(
        "--out",
        default="mkdocs.subset.yml",
        help="Path to the output temporary config file.",
    )
    parser.add_argument(
        "--clean", action="store_true", help="Build a clean version (no dirty reload)."
    )
    parser.add_argument(
        "--port", default="8000", help="Port to serve on (default: 8000)."
    )

    args = parser.parse_args()

    # Resolve alias
    target_section = args.section
    if target_section.lower() in ALIAS_MAP:
        target_section = ALIAS_MAP[target_section.lower()]
        print(f"Resolved alias '{args.section}' to '{target_section}'")

    try:
        with open(args.config) as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
    except FileNotFoundError:
        print(f"Error: Could not find {args.config}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        sys.exit(1)

    if "nav" not in config:
        print("Error: 'nav' section not found in mkdocs.yml")
        sys.exit(1)

    original_nav = config["nav"]
    new_nav = []

    # Always keep "Get started" or root index
    for item in original_nav:
        if isinstance(item, dict):
            key = list(item.keys())[0]
            value = item[key]
            if "get started" in key.lower() or (
                isinstance(value, str) and value == "index.md"
            ):
                new_nav.append(item)

    # Find the requested section
    found_section = find_section(original_nav, target_section)

    if not found_section:
        print(f"Error: No section matching '{target_section}' found in nav.")
        print(f"Available aliases: {', '.join(ALIAS_MAP.keys())}")
        sys.exit(1)

    new_nav.append(found_section)
    config["nav"] = new_nav

    # --- Exclusion Logic ---

    # 1. Identify kept paths
    kept_paths = get_all_paths(new_nav)
    kept_roots = set()
    for p in kept_paths:
        # Handle paths like 'langchain/index.md' -> 'langchain'
        parts = p.split("/")
        if len(parts) > 0:
            kept_roots.add(parts[0])

    print(f"Kept top-level directories: {kept_roots}")

    # 2. Identify all top-level docs directories
    docs_dir = "docs"
    if not os.path.exists(docs_dir):
        print(f"Warning: {docs_dir} directory not found. Skipping exclusion logic.")
    else:
        all_roots = [
            d for d in os.listdir(docs_dir) if os.path.isdir(os.path.join(docs_dir, d))
        ]

        # 3. Define always kept directories (assets, snippets, etc.)
        always_keep = {
            "_snippets",
            "static",
            "stylesheets",
            "javascripts",
            "templates",
            "overrides",
            "__pycache__",
        }

        # 4. Calculate excludes
        to_exclude = []
        for root in all_roots:
            if root not in kept_roots and root not in always_keep:
                to_exclude.append(f"{root}/**/*")

        if to_exclude:
            print(f"Excluding {len(to_exclude)} directories to speed up build.")

            # Add mkdocs-exclude plugin
            if "plugins" not in config:
                config["plugins"] = []

            # Check if exclude plugin is already present
            exclude_plugin = None
            for p in config["plugins"]:
                if isinstance(p, dict) and "exclude" in p:
                    exclude_plugin = p
                    break

            if exclude_plugin:
                if "glob" not in exclude_plugin["exclude"]:
                    exclude_plugin["exclude"]["glob"] = []
                exclude_plugin["exclude"]["glob"].extend(to_exclude)
            else:
                config["plugins"].append({"exclude": {"glob": to_exclude}})

    # Write the new config
    with open(args.out, "w") as f:
        yaml.dump(config, f, Dumper=CustomDumper, sort_keys=False)

    print(f"Generated {args.out}")

    # Run mkdocs serve
    cmd = [
        "uv",
        "run",
        "--no-sync",
        "python",
        "-m",
        "mkdocs",
        "serve",
        "-f",
        args.out,
        "-a",
        f"localhost:{args.port}",
    ]
    if not args.clean:
        cmd.append("--dirty")

    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        if os.path.exists(args.out):
            os.remove(args.out)
            print(f"Removed {args.out}")


if __name__ == "__main__":
    main()
