"""MkDocs Documentation Subset Server.

Create and serve a subset of the Python reference documentation.

Faster build times for development and testing.

Usage:
    python serve_subset.py langgraph  # Serve only the LangGraph section
"""  # noqa: INP001

import argparse
import subprocess
import sys
from collections import deque
from pathlib import Path

import yaml

ALIAS_MAP = {
    "deepagents": "Deep Agents",
    "core": "langchain-core",
    "community": "langchain-community",
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


def env_constructor(loader: yaml.SafeLoader, node: yaml.Node) -> EnvTag:
    """YAML constructor for `!ENV` tags.

    Args:
        loader: YAML loader instance.
        node: YAML node to construct.

    Returns:
        EnvTag: Wrapped environment tag value.
    """
    if isinstance(node, yaml.SequenceNode):
        value: str | list = loader.construct_sequence(node)
    elif isinstance(node, (yaml.ScalarNode, yaml.MappingNode)):
        value = loader.construct_scalar(node)
    else:
        msg = f"Unsupported node type for !ENV tag: {type(node)}"
        raise TypeError(msg)
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


# Register with SafeLoader
yaml.SafeLoader.add_constructor("!ENV", env_constructor)


class CustomDumper(yaml.SafeDumper):
    """Custom YAML dumper that preserves special YAML tags from `mkdocs.yml`.

    When this script reads the original `mkdocs.yml` file and modifies it (e.g.,
    creating a subset navigation), it needs to write the modified configuration back to
    a new YAML file while preserving the original custom tags.

    Without this, tags like `!ENV [ENABLE_INSIDERS_PLUGINS, false]` would be lost during
    the YAML serialization process.

    Example:
        ```yaml
        - group:
            enabled: !ENV [ENABLE_INSIDERS_PLUGINS, false]
        ```

    This dumper ensures the `!ENV` tag is preserved in the output `mkdocs.subset.yml`
    file so MkDocs can still process environment variables correctly.
    """


CustomDumper.add_representer(EnvTag, env_representer)

# --- End Custom YAML handling ---


def find_section(nav: list, target: str) -> dict | None:
    """Search for a section in the nav using BFS.

    Use BFS since we're typically not building a deep subset. Resolves issues where some
    subsections share names with higher-level sections (e.g. `langsmith` under
    langchain-classic).

    Args:
        nav: The nav from mkdocs.yml
        target: The section name to search for (case-insensitive)

    Returns:
        The matching navigation section as a `dict`, or `None` if not found

    Example:
        ```python
        nav = [
            {'Home': 'index.md'},
            {'LangGraph':
                [
                    {'Introduction': 'langgraph/index.md'}
                ]
            }
        ]

        find_section(nav, 'langgraph')
        # {'LangGraph':
        #   [
        #       {'Introduction': 'langgraph/index.md'}
        #   ]
        # }
        ```
    """
    target = target.lower()

    # BFS queue: (nav_item, path_for_debugging)
    queue: deque[tuple[dict | list | str, list[str]]] = deque()

    # Initialize queue with top-level items
    if isinstance(nav, list):
        for item in nav:
            queue.append((item, []))
    else:
        queue.append((nav, []))

    while queue:
        current_nav, path = queue.popleft()

        if isinstance(current_nav, dict):
            key = next(iter(current_nav.keys()))
            current_path = [*path, key]

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
    """Recursively extract all file paths from a nav item.

    Traverses through the given nav item and collects all file paths (as string values)
    from nested lists and dictionaries. Used to determine which files are included in a
    documentation subset.

    Args:
        nav_item: A navigation item which can be a list, dict, or string

    Returns:
        List of file paths found in the navigation structure

    Example:
        ```python
        nav = {
            'LangGraph': [
                {'Introduction': 'langgraph/index.md'},
                'langgraph/tutorial.md'
            ]
        }

        get_all_paths(nav)
        # ['langgraph/index.md', 'langgraph/tutorial.md']
        ```
    """
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


def main() -> None:
    """Main entry point for the documentation subset server.

    Parses command-line arguments, generates a subset of the MkDocs configuration
    based on the specified section, and serves the documentation.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "section",
        help=(
            "The section of the nav to build (e.g., 'LangGraph', 'Integrations'). "
            "Case-insensitive."
        ),
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

    # Validate args
    if not args.port.isdigit() or not (1024 <= int(args.port) <= 65535):  # noqa: PLR2004
        print(
            f"Error: Invalid port '{args.port}'. Must be a number between 1024-65535."
        )
        sys.exit(1)
    if not args.out.endswith(".yml"):
        print(f"Error: Output file must have a .yml extension. Got: {args.out}")
        sys.exit(1)

    # Resolve alias
    target_section: str = args.section
    if target_section.lower() in ALIAS_MAP:
        target_section = ALIAS_MAP[target_section.lower()]
        print(f"Resolved alias '{args.section}' to '{target_section}'")

    # Load the original mkdocs.yml
    try:
        with Path(args.config).open() as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
    except FileNotFoundError:
        print(f"Error: Could not find {args.config}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        sys.exit(1)

    # Validate nav presence
    if "nav" not in config:
        print("Error: 'nav' section not found in mkdocs.yml")
        sys.exit(1)

    original_nav: list = config["nav"]
    new_nav = []

    # Always keep "Get started" / root index
    for item in original_nav:
        if isinstance(item, dict):
            key = next(iter(item.keys()))
            value = item[key]
            if "get started" in key.lower() or (
                isinstance(value, str) and value == "index.md"
            ):
                new_nav.append(item)

    # Find the requested section
    found_section = find_section(original_nav, target_section)

    if not found_section:
        print(f"Error: No section matching '{target_section}' found in nav.")
        sys.exit(1)

    new_nav.append(found_section)
    config["nav"] = new_nav  # Replace nav with new subset

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
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print(f"Warning: {docs_dir} directory not found. Skipping exclusion logic.")
    else:
        all_roots = [d.name for d in docs_dir.iterdir() if d.is_dir()]

        # 3. Directories to keep always (assets, snippets, etc.)
        always_keep = {
            "_snippets",
            "javascripts",
            "static",
            "stylesheets",
            "overrides",
            "templates",
        }

        # 4. Calculate excludes
        to_exclude = [
            f"{root}/**/*"
            for root in all_roots
            if root not in kept_roots and root not in always_keep
        ]

        if to_exclude:
            print(f"Excluding {len(to_exclude)} directories.")

            # Configure mkdocs-exclude plugin to exclude paths
            if "plugins" not in config:
                # Ensure plugins list exists
                config["plugins"] = []
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

    # Write the new mkdocs.yml using the output name
    with Path(args.out).open("w") as f:
        yaml.dump(
            config,
            f,
            Dumper=CustomDumper,  # Use custom dumper to preserve tags
            sort_keys=False,  # Preserve key order
        )
    print(f"Generated {args.out}")

    # Serve the documentation subset
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
        subprocess.run(cmd, check=True)  # noqa: S603
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        output_path = Path(args.out)
        if output_path.exists():
            # Cleanup temporary config file
            output_path.unlink()
            print(f"Removed {args.out}")


if __name__ == "__main__":
    main()
