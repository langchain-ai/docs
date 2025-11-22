#!/usr/bin/env python3
"""Check `langchain_core` re-exports in `langchain`.

1. Fetch latest releases of `langchain_core` and `langchain` from PyPI
2. Introspect all public `__init__` files in `langchain`
3. Identify members that are re-exported from `langchain_core`
4. Store results in `import_mappings.json`

Results used to identify inbound docs that incorrectly include `langchain_core` imports
when they should import from `langchain` instead.
"""

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def get_package_version_after_install(temp_dir: Path, package_name: str) -> str:
    """Get version of installed package using uv pip show."""
    try:
        uv_path = shutil.which("uv")
        if not uv_path:
            return "unknown"

        result = subprocess.run(  # noqa: S603
            [uv_path, "pip", "show", package_name],
            capture_output=True,
            text=True,
            check=True,
            env={**os.environ, "PYTHONPATH": str(temp_dir)},
        )

        for line in result.stdout.split("\n"):
            if line.startswith("Version:"):
                return line.split(":")[1].strip()
    except Exception:  # noqa: BLE001, S110
        pass
    return "unknown"


def install_packages(temp_dir: Path, packages: list[str]) -> None:
    """Install packages in the temporary directory."""

    def _raise_uv_not_found() -> None:
        msg = "uv not found in PATH"
        raise FileNotFoundError(msg)

    uv_path = shutil.which("uv")
    if not uv_path:
        _raise_uv_not_found()

    assert uv_path is not None  # noqa: S101
    uv_cmd = [
        uv_path,
        "pip",
        "install",
        "--target",
        str(temp_dir),
        "--no-deps",  # (Avoid conflicts)
        *packages,
    ]

    print(f"Installing packages: {packages}")
    result = subprocess.run(uv_cmd, check=False, capture_output=True, text=True)  # noqa: S603
    if result.returncode != 0:
        print(f"Error installing packages: {result.stderr}")
        msg = f"Failed to install packages: {result.stderr}"
        raise Exception(msg)  # noqa: TRY002


def find_init_files(package_path: Path) -> list[Path]:
    """Find all `__init__` files in `langchain`."""
    init_files: list[Path] = []

    langchain_dir = package_path / "langchain"
    if not langchain_dir.exists():
        print(f"langchain directory not found at {langchain_dir}")
        return init_files

    # Recursively find all __init__.py files
    for init_file in langchain_dir.rglob("__init__.py"):
        # Skip private/internal modules (those starting with _)
        parts = init_file.relative_to(langchain_dir).parts[:-1]  # Exclude __init__.py
        if any(part.startswith("_") and part != "__init__.py" for part in parts):
            continue
        init_files.append(init_file)

    return init_files


def analyze_init_file(init_file: Path) -> dict[str, Any]:
    """Analyze an `__init__` file to find `langchain_core` re-exports."""
    try:
        with init_file.open(encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        langchain_core_imports = {}
        all_exports = []

        class ImportVisitor(ast.NodeVisitor):
            def visit_ImportFrom(self, node):
                if node.module and node.module.startswith("langchain_core"):
                    for alias in node.names:
                        # The name as it appears in this module (either alias or original)
                        local_name = alias.asname if alias.asname else alias.name

                        # Store the import mapping
                        langchain_core_imports[local_name] = {
                            "module": node.module,
                            "original_name": alias.name,
                        }

            def visit_Assign(self, node):
                # Check for __all__ assignments
                for target in node.targets:
                    # Only handle items that are accessible
                    if (
                        isinstance(target, ast.Name)
                        and target.id == "__all__"
                        and isinstance(node.value, ast.List)
                    ):
                        all_exports.extend(
                            elt.value
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant)
                        )

        visitor = ImportVisitor()
        visitor.visit(tree)

        # Find which imported items are also exported
        exported_from_core = {}
        for export in all_exports:
            if export in langchain_core_imports:
                exported_from_core[export] = langchain_core_imports[export]

        return {
            "file": str(init_file),
            "langchain_core_imports": langchain_core_imports,
            "all_exports": all_exports,
            "exported_from_core": exported_from_core,
        }

    except (OSError, SyntaxError, ValueError) as e:
        print(f"Error analyzing {init_file}: {e}")
        return {
            "file": str(init_file),
            "error": str(e),
            "langchain_core_imports": {},
            "all_exports": [],
            "exported_from_core": {},
        }


def main():
    """Check import mappings."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        install_packages(temp_path, ["langchain", "langchain_core"])
        sys.path.insert(0, str(temp_path))

        # Get versions after installation
        langchain_version = get_package_version_after_install(temp_path, "langchain")
        langchain_core_version = get_package_version_after_install(
            temp_path, "langchain_core"
        )

        print(f"Installed langchain version: {langchain_version}")
        print(f"Installed langchain_core version: {langchain_core_version}")

        init_files = find_init_files(temp_path)
        print(f"Found {len(init_files)} __init__.py files")

        results = {
            "metadata": {
                "langchain_version": langchain_version,
                "langchain_core_version": langchain_core_version,
                "total_init_files": len(init_files),
            },
            "analysis": [],
        }

        for init_file in init_files:
            print(f"Analyzing: {init_file}")
            analysis = analyze_init_file(init_file)
            results["analysis"].append(analysis)

        total_core_exports = 0
        modules_with_core_exports = 0

        for analysis in results["analysis"]:
            if analysis.get("exported_from_core"):
                total_core_exports += len(analysis["exported_from_core"])
                modules_with_core_exports += 1

        results["summary"] = {
            "total_langchain_core_reexports": total_core_exports,
            "modules_with_core_reexports": modules_with_core_exports,
        }

        print("\nSummary:")
        print(f"- Total langchain_core re-exports: {total_core_exports}")
        print(f"- Modules with langchain_core re-exports: {modules_with_core_exports}")

        output_file = Path("import_mappings.json")
        with output_file.open("w") as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
