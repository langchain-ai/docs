"""MkDocs Documentation Subset Server.

Create and serve a subset of the Python reference documentation. Uses the
`mkdocs-exclude` plugin to exclude unneeded sections based on the specified nav section.

https://github.com/apenwarr/mkdocs-exclude

## Exclusion strategy

- Analyzes the navigation structure to identify which top-level directories are needed
- Calculates which directories to exclude by comparing all available docs directories
    against the directories referenced in the kept navigation subset
- Always preserves essential directories like `_snippets`, `javascripts`, `static`, etc.

## Plugin configuration

Automatically configures `mkdocs-exclude` by:

- Adding or modifying the `exclude` plugin configuration in the generated
    `mkdocs.subset.yml`
- Using regex patterns to exclude entire directory trees (e.g., `^langchain/.*`)
- Disabling cross-references
- Preserving existing exclude configurations from the original mkdocs.yml (if any)

## Example exclusion process

When serving only the "LangGraph" section:

```txt
Available directories: ['langchain', 'langgraph', 'langsmith', 'integrations']
Kept directories:      ['langgraph']  # From nav analysis
Always keep:           ['_snippets', 'javascripts', 'static', 'stylesheets']
Excluded patterns:     ['^langchain/.*', '^langsmith/.*', '^integrations/.*']
```

The generated mkdocs.subset.yml will include:

```yaml
plugins:
  - exclude:
      regex:
        - ^langchain/.*
        - ^langsmith/.*
        - ^integrations/.*
  # ... other plugins
```

Usage:
    python serve_subset.py langgraph  # Serve only the LangGraph section
"""  # noqa: INP001

import argparse
import socket
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


class CustomDumper(yaml.SafeDumper):
    """Custom YAML dumper that preserves special YAML tags from `mkdocs.yml`.

    When this script reads the original `mkdocs.yml` file and modifies it (e.g.,
    creating a subset navigation), it needs to write the modified configuration back to
    a new YAML file while preserving the original custom tags.

    Without this, tags like `!ENV [VAR_NAME, default]` or
    `!!python/name:material.extensions.emoji.to_svg` would be lost during the YAML
    serialization process.

    This dumper ensures special YAML tags are preserved in the output `mkdocs.subset.yml`
    file so MkDocs can still process them correctly.
    """


CustomDumper.add_representer(EnvTag, env_representer)
CustomDumper.add_representer(PythonNameTag, python_name_representer)

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


def is_port_available(port: int) -> bool:
    """Check if a port is available for binding.

    Args:
        port: Port number to check

    Returns:
        True if port is available, False if in use
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("localhost", port))
            return True
    except OSError:
        return False


def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> int:
    """Find the first available port starting from start_port.

    Args:
        start_port: Port to start checking from
        max_attempts: Maximum number of ports to try

    Returns:
        First available port number

    Raises:
        RuntimeError: If no available port found within max_attempts
    """
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port

    msg = (
        "No available ports found in range "
        f"{start_port}-{start_port + max_attempts - 1}"
    )
    raise RuntimeError(msg)


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

    # Check if requested port is available, find alternative if not
    requested_port = int(args.port)
    if not is_port_available(requested_port):
        print(f"Port {requested_port} is already in use.")
        try:
            available_port = find_available_port(requested_port)
            print(f"Using available port {available_port} instead.")
            actual_port = str(available_port)
        except RuntimeError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        actual_port = args.port
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
            print(f"Excluding patterns: {to_exclude}")
            # Try using explicit regex patterns instead of glob patterns
            regex_patterns = []
            for pattern in to_exclude:
                # Convert glob patterns to regex
                # langchain/**/* -> ^langchain/.*
                root = pattern.split("/")[0]
                regex_patterns.append(f"^{root}/.*")

            # Configure mkdocs-exclude plugin to exclude paths
            if "plugins" not in config:
                config["plugins"] = []
            exclude_plugin = None
            for p in config["plugins"]:
                if isinstance(p, dict) and "exclude" in p:
                    exclude_plugin = p
                    break
            if exclude_plugin:
                if "regex" not in exclude_plugin["exclude"]:
                    exclude_plugin["exclude"]["regex"] = []
                exclude_plugin["exclude"]["regex"].extend(regex_patterns)
            else:
                # Always insert exclude plugin at the very beginning
                new_exclude_plugin = {"exclude": {"regex": regex_patterns}}
                config["plugins"].insert(0, new_exclude_plugin)

    # --- Remove modules from preload_modules in original mkdocs.yml ---

    # Find and update mkdocstrings plugin configuration
    for plugin in config.get("plugins", []):
        if isinstance(plugin, dict) and "mkdocstrings" in plugin:
            mkdocstrings_config = plugin["mkdocstrings"]
            handlers = mkdocstrings_config.get("handlers", {})
            python_handler = handlers.get("python", {})
            options = python_handler.get("options", {})

            if "preload_modules" in options:
                # Disable preloading modules
                original_preload = options["preload_modules"]
                options["preload_modules"] = []
                print(f"Filtered preload_modules: {original_preload} → []")

            # Disable signature cross-references
            options["signature_crossrefs"] = False

            # Disable auto-discovery of packages to prevent cross-references
            options["show_inheritance_diagram"] = False
            options["allow_inspection"] = False

            # Disable imports and inventory that might cause cross-package resolution
            # issues when serving subsets
            options["enable_inventory"] = False
            handlers["python"]["import"] = []

            break

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
        f"localhost:{actual_port}",
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
